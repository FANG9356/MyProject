package handlers

import (
	"database/sql"
	"encoding/json"
	"strings"
	"testing"
	"time"

	_ "github.com/mattn/go-sqlite3"
)


func setupMaintenanceE2ETestDB(t *testing.T) (*sql.DB, *sql.DB) {
	master, err := sql.Open("sqlite3", ":memory:")
	if err != nil {
		t.Fatalf("failed to open master in-memory db: %v", err)
	}
	master.SetMaxOpenConns(1)


	if _, err := master.Exec(`CREATE TABLE IF NOT EXISTS admins (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT UNIQUE,
		password TEXT,
		role TEXT DEFAULT 'services',
		profile_image TEXT DEFAULT '',
		email TEXT,
		line_user_id TEXT,
		promptpay_id TEXT,
		bank_account TEXT DEFAULT '',
		account_name TEXT DEFAULT ''
	)`); err != nil {
		t.Fatalf("failed to create admins table: %v", err)
	}


	if _, err := master.Exec(`INSERT INTO admins (id, username, role, promptpay_id, bank_account, account_name)
		VALUES (1, 'superadmin', 'superadmin', '0812345678', '123-4-56789-0', 'หอพักสุขสบาย')`); err != nil {
		t.Fatalf("failed to insert test superadmin: %v", err)
	}


	if _, err := master.Exec(`CREATE TABLE IF NOT EXISTS sync_snapshots (
		snapshot_id TEXT PRIMARY KEY,
		account_id INTEGER,
		version INTEGER,
		payload TEXT,
		checksum TEXT,
		size INTEGER,
		device_id TEXT,
		created_at TEXT,
		created_by_admin_id INTEGER,
		UNIQUE(account_id, version)
	)`); err != nil {
		t.Fatalf("failed to create sync_snapshots table: %v", err)
	}


	InitializeLineIntegration(master)


	seedInitialSnapshot(t, master, 1)


	tenant, err := sql.Open("sqlite3", ":memory:")
	if err != nil {
		t.Fatalf("failed to open tenant in-memory db: %v", err)
	}
	tenant.SetMaxOpenConns(1)
	InitializeTenantDatabase(tenant)
	ensureLineTenantSchema(tenant)

	return master, tenant
}


func seedInitialSnapshot(t *testing.T, master *sql.DB, accountID int) {
	payload := map[string]interface{}{
		"snapshotID":  "init-snapshot-01",
		"accountID":   accountID,
		"version":     1,
		"createdAt":   "2026-10-01T00:00:00Z",
		"deviceID":    "ios-admin-device",
		"rooms":       []interface{}{},
		"tenants":     []interface{}{},
		"maintenance": []interface{}{},
		"payments":    []interface{}{},
	}
	raw, err := json.Marshal(payload)
	if err != nil {
		t.Fatalf("failed to marshal initial snapshot: %v", err)
	}
	if _, err := master.Exec(`INSERT INTO sync_snapshots
		(snapshot_id, account_id, version, payload, checksum, size, device_id, created_at, created_by_admin_id)
		VALUES ('init-snapshot-01', ?, 1, ?, '', ?, 'ios-admin-device', '2026-10-01T00:00:00Z', 1)`,
		accountID, string(raw), len(raw)); err != nil {
		t.Fatalf("failed to seed initial snapshot: %v", err)
	}
}


func TestMaintenanceE2E_PaidFlow_QuoteApprovalToPaymentAndCompletion(t *testing.T) {
	master, tenant := setupMaintenanceE2ETestDB(t)
	defer func() {
		time.Sleep(50 * time.Millisecond)
		master.Close()
		tenant.Close()
	}()


	if _, err := tenant.Exec(`INSERT INTO rooms (room_number, room_type) VALUES ('101', 'Standard')`); err != nil {
		t.Fatalf("failed to insert room: %v", err)
	}
	if _, err := tenant.Exec(`INSERT INTO users (full_name, room_number, status, line_user_id, phone)
		VALUES ('นายสมชาย มั่นคง', '101', 'กำลังพักอาศัย', 'line-u101', '0811111111')`); err != nil {
		t.Fatalf("failed to insert user: %v", err)
	}


	res, err := tenant.Exec(`INSERT INTO maintenances (room_number, issue, status, cost, reported_at)
		VALUES ('101', 'ก๊อกน้ำอ่างล้างหน้ารั่ว ซึมลงพื้น', 'รอดำเนินการ', 0, '2026-10-14 09:00:00')`)
	if err != nil {
		t.Fatalf("failed to report maintenance: %v", err)
	}
	maintIDInt, _ := res.LastInsertId()
	maintID := "1"


	var status string
	var cost float64
	tenant.QueryRow("SELECT status, cost FROM maintenances WHERE id = ?", maintIDInt).Scan(&status, &cost)
	if status != "รอดำเนินการ" || cost != 0 {
		t.Fatalf("unexpected initial state: status=%q, cost=%v", status, cost)
	}


	newCost := 850.00
	if err := validateMaintenanceAppTransition("รอดำเนินการ", "กำลังติดต่อช่าง", newCost, false); err != nil {
		t.Fatalf("transition รอดำเนินการ -> กำลังติดต่อช่าง should be allowed: %v", err)
	}
	if _, err := tenant.Exec("UPDATE maintenances SET status = 'กำลังติดต่อช่าง', cost = ? WHERE id = ?", newCost, maintIDInt); err != nil {
		t.Fatalf("failed to update status to กำลังติดต่อช่าง: %v", err)
	}


	if err := validateMaintenanceAppTransition("กำลังติดต่อช่าง", "รออนุมัติค่าใช้จ่าย", newCost, false); err != nil {
		t.Fatalf("transition กำลังติดต่อช่าง -> รออนุมัติค่าใช้จ่าย should be allowed: %v", err)
	}
	if !maintenanceHasLineRecipient(tenant, maintID) {
		t.Fatal("maintenance should have a linked LINE recipient")
	}


	if err := validateMaintenanceAppTransition("รออนุมัติค่าใช้จ่าย", "กำลังซ่อม", newCost, false); err == nil {
		t.Fatal("paid repair must not skip quote approval and payment")
	}

	if _, err := tenant.Exec("UPDATE maintenances SET status = 'รออนุมัติค่าใช้จ่าย' WHERE id = ?", maintIDInt); err != nil {
		t.Fatalf("failed to update status to รออนุมัติค่าใช้จ่าย: %v", err)
	}


	handleMaintenanceQuoteDecision(master, tenant, 1, "reply-tok-101", "line-u101", maintID, true)


	var quoteApprovedAt string
	tenant.QueryRow("SELECT status, cost, quote_approved_at FROM maintenances WHERE id = ?", maintIDInt).Scan(&status, &cost, &quoteApprovedAt)
	if status != "รอตรวจสอบชำระเงิน" {
		t.Fatalf("expected status 'รอตรวจสอบชำระเงิน' after approval, got %q", status)
	}
	if quoteApprovedAt == "" {
		t.Fatal("expected quote_approved_at to be populated after approval")
	}


	var botState string
	tenant.QueryRow("SELECT bot_state FROM users WHERE line_user_id = 'line-u101'").Scan(&botState)
	if botState != "pay_maint_1" {
		t.Fatalf("expected bot_state 'pay_maint_1', got %q", botState)
	}


	var outboxCount int
	var outboxStatus, outboxRoom, outboxIssue string
	var outboxCost float64
	if err := master.QueryRow(`SELECT status, room_number, issue, cost FROM line_notification_outbox
		WHERE account_id = 1 AND line_user_id = 'line-u101' AND maintenance_record_id = '1'`).Scan(
		&outboxStatus, &outboxRoom, &outboxIssue, &outboxCost); err != nil {
		t.Fatalf("expected outbox notification for approved quote: %v", err)
	}
	if outboxRoom != "101" || outboxCost != newCost {
		t.Fatalf("outbox notification mismatch: room=%q, cost=%v", outboxRoom, outboxCost)
	}


	var latestVersion int
	var latestDevice, latestPayload string
	if err := master.QueryRow(`SELECT version, device_id, payload FROM sync_snapshots
		WHERE account_id = 1 ORDER BY version DESC LIMIT 1`).Scan(&latestVersion, &latestDevice, &latestPayload); err != nil {
		t.Fatalf("failed to query sync_snapshots: %v", err)
	}
	if latestVersion < 2 || latestDevice != "line-bot" {
		t.Fatalf("expected snapshot version >= 2 from line-bot, got version=%d device=%q", latestVersion, latestDevice)
	}


	var snapData map[string]interface{}
	if err := json.Unmarshal([]byte(latestPayload), &snapData); err != nil {
		t.Fatalf("failed to unmarshal snapshot payload: %v", err)
	}
	maintList, ok := snapData["maintenance"].([]interface{})
	if !ok || len(maintList) == 0 {
		t.Fatal("expected maintenance items in snapshot payload")
	}
	firstMaint := maintList[0].(map[string]interface{})
	if firstMaint["status"] != "รอตรวจสอบชำระเงิน" {
		t.Fatalf("expected snapshot status 'รอตรวจสอบชำระเงิน', got %v", firstMaint["status"])
	}
	if firstMaint["quoteApprovedAt"] == "" {
		t.Fatal("expected snapshot quoteApprovedAt to be present")
	}


	slipPath := "maint_slip_101.jpg"
	slipPayload := "00020101021229370016A000000677010111011300668123456785802TH53037645406850.005802TH6304ABCD"
	if _, err := tenant.Exec(`UPDATE maintenances SET slip_path = ?, slip_payload = ?, last_updated = ? WHERE id = ?`,
		slipPath, slipPayload, time.Now().UTC().Format(time.RFC3339Nano), maintIDInt); err != nil {
		t.Fatalf("failed to update slip on maintenance: %v", err)
	}
	tenant.Exec("UPDATE users SET bot_state = 'none' WHERE line_user_id = 'line-u101'")


	if err := validateMaintenanceAppTransition("รอตรวจสอบชำระเงิน", "กำลังซ่อม", newCost, true); err != nil {
		t.Fatalf("transition รอตรวจสอบชำระเงิน -> กำลังซ่อม should be allowed after payment: %v", err)
	}
	if _, err := tenant.Exec("UPDATE maintenances SET status = 'กำลังซ่อม' WHERE id = ?", maintIDInt); err != nil {
		t.Fatalf("failed to update status to กำลังซ่อม: %v", err)
	}


	if err := validateMaintenanceAppTransition("กำลังซ่อม", "เสร็จสิ้น", newCost, true); err != nil {
		t.Fatalf("transition กำลังซ่อม -> เสร็จสิ้น should be allowed: %v", err)
	}
	resolvedAt := time.Now().UTC().Format(time.RFC3339)
	if _, err := tenant.Exec("UPDATE maintenances SET status = 'เสร็จสิ้น', resolved_at = ? WHERE id = ?", resolvedAt, maintIDInt); err != nil {
		t.Fatalf("failed to update status to เสร็จสิ้น: %v", err)
	}


	var finalStatus, finalSlip, finalResolved string
	tenant.QueryRow("SELECT status, slip_path, resolved_at FROM maintenances WHERE id = ?", maintIDInt).Scan(
		&finalStatus, &finalSlip, &finalResolved,
	)
	if finalStatus != "เสร็จสิ้น" || finalSlip != slipPath || finalResolved == "" {
		t.Fatalf("final state invalid: status=%q, slip=%q, resolved_at=%q", finalStatus, finalSlip, finalResolved)
	}

	_ = outboxCount
}


func TestMaintenanceE2E_PaidFlow_QuoteRejection_IsTerminal(t *testing.T) {
	master, tenant := setupMaintenanceE2ETestDB(t)
	defer func() {
		time.Sleep(50 * time.Millisecond)
		master.Close()
		tenant.Close()
	}()


	tenant.Exec(`INSERT INTO rooms (room_number, room_type) VALUES ('102', 'Deluxe')`)
	tenant.Exec(`INSERT INTO users (full_name, room_number, status, line_user_id)
		VALUES ('นางสาววิภา ใจดี', '102', 'กำลังพักอาศัย', 'line-u102')`)


	cost := 1500.00
	res, err := tenant.Exec(`INSERT INTO maintenances (room_number, issue, status, cost, reported_at)
		VALUES ('102', 'แอร์ไม่เย็น มีเสียงดังผิดปกติ', 'รออนุมัติค่าใช้จ่าย', ?, '2026-10-14 10:00:00')`, cost)
	if err != nil {
		t.Fatalf("failed to insert maintenance: %v", err)
	}
	maintIDInt, _ := res.LastInsertId()
	maintID := "1"


	handleMaintenanceQuoteDecision(master, tenant, 1, "reply-tok-102", "line-u102", maintID, false)


	var status, quoteApprovedAt string
	tenant.QueryRow("SELECT status, quote_approved_at FROM maintenances WHERE id = ?", maintIDInt).Scan(&status, &quoteApprovedAt)
	if status != "ปฏิเสธค่าใช้จ่าย" {
		t.Fatalf("expected status 'ปฏิเสธค่าใช้จ่าย', got %q", status)
	}
	if quoteApprovedAt != "" {
		t.Fatalf("expected quote_approved_at to be empty for rejected quote, got %q", quoteApprovedAt)
	}


	var eventKey string
	if err := master.QueryRow(`SELECT event_key FROM line_notification_outbox
		WHERE account_id = 1 AND line_user_id = 'line-u102' AND maintenance_record_id = '1'`).Scan(&eventKey); err != nil {
		t.Fatalf("expected outbox record for rejected quote: %v", err)
	}
	if !strings.Contains(eventKey, "maintenance-quote-rejected") {
		t.Fatalf("expected eventKey to contain 'maintenance-quote-rejected', got %q", eventKey)
	}


	if err := validateMaintenanceAppTransition("ปฏิเสธค่าใช้จ่าย", "กำลังซ่อม", cost, false); err == nil {
		t.Fatal("transition from ปฏิเสธค่าใช้จ่าย to กำลังซ่อม must be rejected")
	}


	if err := validateMaintenanceAppTransition("ปฏิเสธค่าใช้จ่าย", "เสร็จสิ้น", cost, false); err == nil {
		t.Fatal("transition from ปฏิเสธค่าใช้จ่าย to เสร็จสิ้น must be rejected")
	}
}


func TestMaintenanceE2E_FreeFlow_SkipsQuoteAndPayment(t *testing.T) {
	master, tenant := setupMaintenanceE2ETestDB(t)
	defer master.Close()
	defer tenant.Close()

	tenant.Exec(`INSERT INTO rooms (room_number, room_type) VALUES ('103', 'Standard')`)
	tenant.Exec(`INSERT INTO users (full_name, room_number, status, line_user_id)
		VALUES ('นายอนุชา รักสงบ', '103', 'กำลังพักอาศัย', 'line-u103')`)

	res, err := tenant.Exec(`INSERT INTO maintenances (room_number, issue, status, cost, reported_at)
		VALUES ('103', 'หลอดไฟระเบียงขาด', 'รอดำเนินการ', 0, '2026-10-14 11:00:00')`)
	if err != nil {
		t.Fatalf("failed to insert maintenance: %v", err)
	}
	maintIDInt, _ := res.LastInsertId()


	if err := validateMaintenanceAppTransition("รอดำเนินการ", "กำลังติดต่อช่าง", 0, false); err != nil {
		t.Fatalf("expected allowed transition: %v", err)
	}
	tenant.Exec("UPDATE maintenances SET status = 'กำลังติดต่อช่าง' WHERE id = ?", maintIDInt)


	if err := validateMaintenanceAppTransition("กำลังติดต่อช่าง", "กำลังซ่อม", 0, false); err != nil {
		t.Fatalf("free repair should bypass quote approval and payment: %v", err)
	}
	tenant.Exec("UPDATE maintenances SET status = 'กำลังซ่อม' WHERE id = ?", maintIDInt)


	if err := validateMaintenanceAppTransition("กำลังซ่อม", "เสร็จสิ้น", 0, false); err != nil {
		t.Fatalf("free repair should complete: %v", err)
	}
	tenant.Exec("UPDATE maintenances SET status = 'เสร็จสิ้น', resolved_at = ? WHERE id = ?",
		time.Now().UTC().Format(time.RFC3339), maintIDInt)


	if err := validateMaintenanceAppTransition("กำลังติดต่อช่าง", "กำลังซ่อม", 350.00, false); err == nil {
		t.Fatal("paid repair must not skip quote approval and payment")
	}
}


func TestMaintenanceE2E_Security_UnauthorizedLineUserCannotApprove(t *testing.T) {
	master, tenant := setupMaintenanceE2ETestDB(t)
	defer func() {
		time.Sleep(50 * time.Millisecond)
		master.Close()
		tenant.Close()
	}()


	tenant.Exec(`INSERT INTO rooms (room_number, room_type) VALUES ('104', 'Standard')`)
	tenant.Exec(`INSERT INTO users (full_name, room_number, status, line_user_id)
		VALUES ('นายกฤษณะ มีทรัพย์', '104', 'กำลังพักอาศัย', 'line-u104')`)


	tenant.Exec(`INSERT INTO rooms (room_number, room_type) VALUES ('105', 'Standard')`)
	tenant.Exec(`INSERT INTO users (full_name, room_number, status, line_user_id)
		VALUES ('นางสาวสิรินทร์ สมบูรณ์', '105', 'กำลังพักอาศัย', 'line-u105')`)


	tenant.Exec(`INSERT INTO rooms (room_number, room_type) VALUES ('106', 'Standard')`)
	tenant.Exec(`INSERT INTO users (full_name, room_number, status, line_user_id)
		VALUES ('นายธนวัฒน์ อดีตผู้พัก', '106', 'ย้ายออกแล้ว', 'line-u106')`)


	res, err := tenant.Exec(`INSERT INTO maintenances (room_number, issue, status, cost, reported_at)
		VALUES ('104', 'ลูกบิดประตูห้องน้ำชำรุด', 'รออนุมัติค่าใช้จ่าย', 450.00, '2026-10-14 12:00:00')`)
	if err != nil {
		t.Fatalf("failed to insert maintenance: %v", err)
	}
	maintIDInt, _ := res.LastInsertId()
	maintID := "1"


	handleMaintenanceQuoteDecision(master, tenant, 1, "reply-tok-stranger", "line-unauthorized-stranger", maintID, true)

	var status, quoteApprovedAt string
	tenant.QueryRow("SELECT status, quote_approved_at FROM maintenances WHERE id = ?", maintIDInt).Scan(&status, &quoteApprovedAt)
	if status != "รออนุมัติค่าใช้จ่าย" || quoteApprovedAt != "" {
		t.Fatalf("unauthorized stranger should not modify maintenance: status=%q, approvedAt=%q", status, quoteApprovedAt)
	}


	handleMaintenanceQuoteDecision(master, tenant, 1, "reply-tok-105", "line-u105", maintID, true)

	tenant.QueryRow("SELECT status, quote_approved_at FROM maintenances WHERE id = ?", maintIDInt).Scan(&status, &quoteApprovedAt)
	if status != "รออนุมัติค่าใช้จ่าย" || quoteApprovedAt != "" {
		t.Fatalf("resident from another room should not approve quote: status=%q, approvedAt=%q", status, quoteApprovedAt)
	}


	handleMaintenanceQuoteDecision(master, tenant, 1, "reply-tok-106", "line-u106", maintID, true)

	tenant.QueryRow("SELECT status, quote_approved_at FROM maintenances WHERE id = ?", maintIDInt).Scan(&status, &quoteApprovedAt)
	if status != "รออนุมัติค่าใช้จ่าย" || quoteApprovedAt != "" {
		t.Fatalf("moved-out resident should not approve quote: status=%q, approvedAt=%q", status, quoteApprovedAt)
	}


	handleMaintenanceQuoteDecision(master, tenant, 1, "reply-tok-104", "line-u104", maintID, true)

	tenant.QueryRow("SELECT status, quote_approved_at FROM maintenances WHERE id = ?", maintIDInt).Scan(&status, &quoteApprovedAt)
	if status != "รอตรวจสอบชำระเงิน" || quoteApprovedAt == "" {
		t.Fatalf("legitimate resident approval failed: status=%q, approvedAt=%q", status, quoteApprovedAt)
	}
}


func TestMaintenanceE2E_StaleOrDuplicateDecision_IsIdempotent(t *testing.T) {
	master, tenant := setupMaintenanceE2ETestDB(t)
	defer func() {
		time.Sleep(50 * time.Millisecond)
		master.Close()
		tenant.Close()
	}()

	tenant.Exec(`INSERT INTO rooms (room_number, room_type) VALUES ('107', 'Standard')`)
	tenant.Exec(`INSERT INTO users (full_name, room_number, status, line_user_id)
		VALUES ('นายปิยะพงษ์ สมหมาย', '107', 'กำลังพักอาศัย', 'line-u107')`)

	res, err := tenant.Exec(`INSERT INTO maintenances (room_number, issue, status, cost, reported_at)
		VALUES ('107', 'สายฝักบัวแตก', 'รออนุมัติค่าใช้จ่าย', 300.00, '2026-10-14 13:00:00')`)
	if err != nil {
		t.Fatalf("failed to insert maintenance: %v", err)
	}
	maintIDInt, _ := res.LastInsertId()
	maintID := "1"


	handleMaintenanceQuoteDecision(master, tenant, 1, "reply-tok-first", "line-u107", maintID, true)

	var initialStatus, initialApprovedAt string
	tenant.QueryRow("SELECT status, quote_approved_at FROM maintenances WHERE id = ?", maintIDInt).Scan(&initialStatus, &initialApprovedAt)
	if initialStatus != "รอตรวจสอบชำระเงิน" || initialApprovedAt == "" {
		t.Fatalf("initial approval failed: status=%q", initialStatus)
	}


	handleMaintenanceQuoteDecision(master, tenant, 1, "reply-tok-duplicate", "line-u107", maintID, true)

	var duplicateStatus, duplicateApprovedAt string
	tenant.QueryRow("SELECT status, quote_approved_at FROM maintenances WHERE id = ?", maintIDInt).Scan(&duplicateStatus, &duplicateApprovedAt)
	if duplicateStatus != initialStatus || duplicateApprovedAt != initialApprovedAt {
		t.Fatalf("duplicate approval corrupted data: status=%q vs %q, time=%q vs %q",
			duplicateStatus, initialStatus, duplicateApprovedAt, initialApprovedAt)
	}


	handleMaintenanceQuoteDecision(master, tenant, 1, "reply-tok-reject-after-approve", "line-u107", maintID, false)

	var postRejectStatus string
	tenant.QueryRow("SELECT status FROM maintenances WHERE id = ?", maintIDInt).Scan(&postRejectStatus)
	if postRejectStatus != "รอตรวจสอบชำระเงิน" {
		t.Fatalf("rejection after approval should have been ignored, got %q", postRejectStatus)
	}
}


func TestMaintenanceE2E_ReplayProtection_PreventsSlipReuse(t *testing.T) {
	_, tenant := setupMaintenanceE2ETestDB(t)
	defer tenant.Close()

	payloadSlip := "00020101021229370016A000000677010111011300668123456785802TH53037645406500.005802TH6304XYZW"


	_, err := tenant.Exec(`INSERT INTO maintenances (room_number, issue, status, cost, slip_path, slip_payload)
		VALUES ('108', 'ซ่อมฝ้าเพดาน', 'รอตรวจสอบชำระเงิน', 500.00, 'slip_1.jpg', ?)`, payloadSlip)
	if err != nil {
		t.Fatalf("failed to insert maintenance with slip: %v", err)
	}


	_, err = tenant.Exec(`INSERT INTO maintenances (room_number, issue, status, cost, slip_path, slip_payload)
		VALUES ('109', 'ซ่อมกระจก', 'รอตรวจสอบชำระเงิน', 500.00, 'slip_2.jpg', ?)`, payloadSlip)
	if err == nil {
		t.Fatal("expected unique constraint violation when inserting duplicate slip_payload in maintenances")
	}


	var existingMaintID int
	errCheck := tenant.QueryRow("SELECT id FROM maintenances WHERE slip_payload = ?", payloadSlip).Scan(&existingMaintID)
	if errCheck != nil {
		t.Fatalf("expected to find existing slip_payload in maintenances: %v", errCheck)
	}
}
