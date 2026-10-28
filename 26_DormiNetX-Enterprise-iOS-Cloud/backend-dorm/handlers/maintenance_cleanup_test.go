package handlers

import (
	"database/sql"
	"os"
	"path/filepath"
	"testing"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

func TestRunMaintenanceCleanup(t *testing.T) {

	tempDir, err := os.MkdirTemp("", "dorminet_maint_cleanup_test_*")
	if err != nil {
		t.Fatalf("Failed to create temp dir: %v", err)
	}
	defer os.RemoveAll(tempDir)


	dbPath := filepath.Join(tempDir, "master.db")
	masterDB, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		t.Fatalf("Failed to open master DB: %v", err)
	}
	defer masterDB.Close()


	masterDB.Exec("CREATE TABLE admins (id INTEGER PRIMARY KEY, role TEXT, profile_image TEXT)")
	masterDB.Exec("INSERT INTO admins (id, role, profile_image) VALUES (1, 'superadmin', 'admin_pic.jpg')")

	os.Chdir(tempDir)


	tenantDB, err := GetTenantDB(1)
	if err != nil {
		t.Fatalf("Failed to open tenant DB: %v", err)
	}


	now := time.Now().UTC()
	oldTime := now.Add(-48 * time.Hour).Format(time.RFC3339Nano)
	recentTime := now.Add(-2 * time.Hour).Format(time.RFC3339Nano)


	tenantDB.Exec("INSERT INTO maintenances (id, room_number, issue, status, last_updated) VALUES (1, '101', 'Issue 1', 'ปฏิเสธค่าใช้จ่าย', ?)", oldTime)


	tenantDB.Exec("INSERT INTO maintenances (id, room_number, issue, status, last_updated) VALUES (2, '102', 'Issue 2', 'ปฏิเสธค่าใช้จ่าย', ?)", recentTime)


	tenantDB.Exec("INSERT INTO maintenances (id, room_number, issue, status, last_updated) VALUES (3, '103', 'Issue 3', 'เสร็จสิ้น', ?)", oldTime)


	RunMaintenanceCleanup(masterDB)


	var count int


	tenantDB.QueryRow("SELECT COUNT(*) FROM maintenances WHERE id = 1").Scan(&count)
	if count != 0 {
		t.Errorf("Expected maintenance 1 to be deleted")
	}


	tenantDB.QueryRow("SELECT COUNT(*) FROM maintenances WHERE id = 2").Scan(&count)
	if count != 1 {
		t.Errorf("Expected maintenance 2 to be kept")
	}


	tenantDB.QueryRow("SELECT COUNT(*) FROM maintenances WHERE id = 3").Scan(&count)
	if count != 1 {
		t.Errorf("Expected maintenance 3 to be kept")
	}
}
