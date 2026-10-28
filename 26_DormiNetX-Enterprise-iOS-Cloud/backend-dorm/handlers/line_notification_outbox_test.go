package handlers

import (
	"database/sql"
	"errors"
	"testing"

	_ "github.com/mattn/go-sqlite3"
)

func testMaintenanceNotification(eventKey string) maintenanceStatusNotification {
	return maintenanceStatusNotification{
		EventKey: eventKey, MaintenanceID: "44", LineUserID: "line-one", RoomNumber: "103", Issue: "ไฟดับ",
		Status: "กำลังซ่อม", Cost: 450, ReportedAt: "2026-09-16",
		PaymentMethod: "โอนผ่านธนาคาร", LastUpdated: "2026-09-17T02:30:00Z",
	}
}

func TestMaintenanceNotificationOutboxIsIdempotent(t *testing.T) {
	db, err := sql.Open("sqlite3", ":memory:")
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()
	db.Exec(`CREATE TABLE admins (id INTEGER PRIMARY KEY, promptpay_id TEXT)`)
	InitializeLineIntegration(db)

	for i := 0; i < 2; i++ {
		if err := EnqueueMaintenanceStatusNotification(db, 7, testMaintenanceNotification("maintenance:7:item:updated:status")); err != nil {
			t.Fatal(err)
		}
	}
	var count int
	if err := db.QueryRow(`SELECT COUNT(*) FROM line_notification_outbox`).Scan(&count); err != nil {
		t.Fatal(err)
	}
	if count != 1 {
		t.Fatalf("outbox rows = %d, want 1", count)
	}
}

func TestProcessMaintenanceNotificationMarksSent(t *testing.T) {
	db, _ := sql.Open("sqlite3", ":memory:")
	defer db.Close()
	db.Exec(`CREATE TABLE admins (id INTEGER PRIMARY KEY, promptpay_id TEXT)`)
	InitializeLineIntegration(db)
	if err := EnqueueMaintenanceStatusNotification(db, 7, testMaintenanceNotification("sent-event")); err != nil {
		t.Fatal(err)
	}
	called := 0
	processPendingLineNotifications(db, func(notification maintenanceStatusNotification) error {
		called++
		if notification.LineUserID != "line-one" || notification.RoomNumber != "103" || notification.Issue != "ไฟดับ" || notification.Status != "กำลังซ่อม" {
			t.Fatalf("unexpected notification: %+v", notification)
		}
		if notification.MaintenanceID != "44" || notification.Cost != 450 || notification.ReportedAt != "2026-09-16" || notification.LastUpdated != "2026-09-17T02:30:00Z" {
			t.Fatalf("notification detail was not persisted: %+v", notification)
		}
		return nil
	})
	var deliveryStatus, sentAt string
	if err := db.QueryRow(`SELECT status, sent_at FROM line_notification_outbox WHERE event_key = 'sent-event'`).Scan(&deliveryStatus, &sentAt); err != nil {
		t.Fatal(err)
	}
	if called != 1 || deliveryStatus != "sent" || sentAt == "" {
		t.Fatalf("called=%d status=%q sent_at=%q", called, deliveryStatus, sentAt)
	}
}

func TestProcessMaintenanceNotificationSchedulesRetry(t *testing.T) {
	db, _ := sql.Open("sqlite3", ":memory:")
	defer db.Close()
	db.Exec(`CREATE TABLE admins (id INTEGER PRIMARY KEY, promptpay_id TEXT)`)
	InitializeLineIntegration(db)
	if err := EnqueueMaintenanceStatusNotification(db, 7, testMaintenanceNotification("retry-event")); err != nil {
		t.Fatal(err)
	}
	processPendingLineNotifications(db, func(_ maintenanceStatusNotification) error {
		return errors.New("temporary LINE failure")
	})
	var deliveryStatus, lastError string
	var attempts int
	if err := db.QueryRow(`SELECT status, attempts, last_error FROM line_notification_outbox WHERE event_key = 'retry-event'`).Scan(&deliveryStatus, &attempts, &lastError); err != nil {
		t.Fatal(err)
	}
	if deliveryStatus != "pending" || attempts != 1 || lastError != "temporary LINE failure" {
		t.Fatalf("status=%q attempts=%d error=%q", deliveryStatus, attempts, lastError)
	}
}

func TestInitializeLineIntegrationRecoversClaimedNotification(t *testing.T) {
	db, _ := sql.Open("sqlite3", ":memory:")
	defer db.Close()
	db.Exec(`CREATE TABLE admins (id INTEGER PRIMARY KEY, promptpay_id TEXT)`)
	InitializeLineIntegration(db)
	if err := EnqueueMaintenanceStatusNotification(db, 7, testMaintenanceNotification("event")); err != nil {
		t.Fatal(err)
	}
	if _, err := db.Exec(`UPDATE line_notification_outbox SET status = 'processing'`); err != nil {
		t.Fatal(err)
	}

	InitializeLineIntegration(db)
	var status string
	if err := db.QueryRow(`SELECT status FROM line_notification_outbox WHERE event_key = 'event'`).Scan(&status); err != nil {
		t.Fatal(err)
	}
	if status != "pending" {
		t.Fatalf("status = %q, want pending", status)
	}
}


func TestDuplicateNotificationFromTwoPathsIsPreventedByEventKey(t *testing.T) {
	db, err := sql.Open("sqlite3", ":memory:")
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()
	db.Exec(`CREATE TABLE admins (id INTEGER PRIMARY KEY, promptpay_id TEXT)`)
	InitializeLineIntegration(db)


	sharedEventKey := "maintenance:1:ext-abc:2026-09-18T04:49:00Z:กำลังติดต่อช่าง"
	notification := maintenanceStatusNotification{
		EventKey:      sharedEventKey,
		MaintenanceID: "55",
		LineUserID:    "line-test",
		RoomNumber:    "103",
		Issue:         "หลอดไฟเสีย",
		Status:        "กำลังติดต่อช่าง",
		LastUpdated:   "2026-09-18T04:49:00Z",
	}


	if err := EnqueueMaintenanceStatusNotification(db, 1, notification); err != nil {
		t.Fatalf("first enqueue failed: %v", err)
	}

	if err := EnqueueMaintenanceStatusNotification(db, 1, notification); err != nil {
		t.Fatalf("second enqueue failed: %v", err)
	}

	var count int
	if err := db.QueryRow(`SELECT COUNT(*) FROM line_notification_outbox WHERE event_key = ?`, sharedEventKey).Scan(&count); err != nil {
		t.Fatal(err)
	}
	if count != 1 {
		t.Fatalf("outbox has %d rows for same event_key, want 1 — duplicate notification would be sent", count)
	}


	sendCount := 0
	processPendingLineNotifications(db, func(n maintenanceStatusNotification) error {
		sendCount++
		if n.LineUserID != "line-test" {
			t.Fatalf("unexpected recipient: %s", n.LineUserID)
		}
		return nil
	})
	if sendCount != 1 {
		t.Fatalf("LINE push called %d times for same event, want 1", sendCount)
	}
}


func TestDifferentStatusTransitionGeneratesSeparateOutboxEntries(t *testing.T) {
	db, err := sql.Open("sqlite3", ":memory:")
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()
	db.Exec(`CREATE TABLE admins (id INTEGER PRIMARY KEY, promptpay_id TEXT)`)
	InitializeLineIntegration(db)

	base := maintenanceStatusNotification{
		MaintenanceID: "66",
		LineUserID:    "line-two",
		RoomNumber:    "201",
		Issue:         "น้ำรั่ว",
	}


	n1 := base
	n1.EventKey = "maintenance:1:ext-def:2026-09-18T05:00:00Z:กำลังติดต่อช่าง"
	n1.Status = "กำลังติดต่อช่าง"
	n1.LastUpdated = "2026-09-18T05:00:00Z"
	if err := EnqueueMaintenanceStatusNotification(db, 1, n1); err != nil {
		t.Fatal(err)
	}


	n2 := base
	n2.EventKey = "maintenance:1:ext-def:2026-09-18T05:05:00Z:รออนุมัติค่าใช้จ่าย"
	n2.Status = "รออนุมัติค่าใช้จ่าย"
	n2.LastUpdated = "2026-09-18T05:05:00Z"
	n2.Cost = 500
	if err := EnqueueMaintenanceStatusNotification(db, 1, n2); err != nil {
		t.Fatal(err)
	}

	var count int
	if err := db.QueryRow(`SELECT COUNT(*) FROM line_notification_outbox`).Scan(&count); err != nil {
		t.Fatal(err)
	}
	if count != 2 {
		t.Fatalf("outbox has %d rows, want 2 for two different status events", count)
	}
}

