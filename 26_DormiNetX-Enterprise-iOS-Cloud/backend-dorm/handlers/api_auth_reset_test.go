package handlers

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

func setupTestDBForReset(t *testing.T) *sql.DB {
	dbName := fmt.Sprintf("file:testdb_%d_%d?mode=memory&cache=shared", time.Now().UnixNano(), time.Now().Unix())
	db, err := sql.Open("sqlite3", dbName)
	if err != nil {
		t.Fatalf("Failed to open memory DB: %v", err)
	}
	db.SetMaxOpenConns(1)


	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS admins (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT UNIQUE,
		password TEXT,
		role TEXT DEFAULT 'services',
		profile_image TEXT DEFAULT '',
		email TEXT,
		backup_email TEXT,
		line_user_id TEXT,
		last_active TEXT,
		promptpay_id TEXT,
		dorm_code TEXT,
		payment_type TEXT DEFAULT 'promptpay',
		bank_account TEXT DEFAULT '',
		account_name TEXT DEFAULT '',
		apns_token TEXT DEFAULT ''
	)`)
	if err != nil {
		t.Fatalf("Failed to create admins table: %v", err)
	}


	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS password_resets (
		email TEXT PRIMARY KEY,
		token TEXT,
		expires_at TEXT
	)`)
	if err != nil {
		t.Fatalf("Failed to create password_resets table: %v", err)
	}


	ensureAuthRateLimitTable(db)


	db.Exec("INSERT INTO admins (username, email) VALUES (?, ?)", "testadmin", "test@dorminet.studio")

	return db
}

func TestForgotPasswordRateLimitAndConcurrency(t *testing.T) {
	db := setupTestDBForReset(t)
	defer db.Close()

	handler := HandleForgotPassword(db)

	reqBody := `{"email": "test@dorminet.studio"}`


	var wg sync.WaitGroup
	results := make(chan int, 10)

	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			req := httptest.NewRequest("POST", "/api/forgot-password", bytes.NewBufferString(reqBody))
			req.Header.Set("Content-Type", "application/json")

			req.RemoteAddr = "127.0.0.1:1234"

			w := httptest.NewRecorder()
			handler(w, req)
			results <- w.Code
		}()
	}
	wg.Wait()
	close(results)

	successCount := 0
	rateLimitedCount := 0

	for code := range results {
		if code == http.StatusOK {
			successCount++
		} else if code == http.StatusTooManyRequests {
			rateLimitedCount++
		}
	}

	if successCount == 0 {
		t.Errorf("Expected at least one success, got %d", successCount)
	}


	var count int
	err := db.QueryRow("SELECT COUNT(*) FROM password_resets WHERE email = ?", "test@dorminet.studio").Scan(&count)
	if err != nil {
		t.Fatalf("Failed to query DB: %v", err)
	}

	if count != 1 {
		t.Errorf("Expected exactly 1 OTP row, got %d", count)
	}
}

func TestVerifyOTPRateLimitAndExpiry(t *testing.T) {
	db := setupTestDBForReset(t)
	defer db.Close()

	handler := HandleVerifyOTP(db)

	email := "test@dorminet.studio"
	otp := "123456"


	expiresAt := time.Now().Add(15 * time.Minute).Format(time.RFC3339)
	db.Exec("INSERT INTO password_resets (email, token, expires_at) VALUES (?, ?, ?)", email, otp, expiresAt)


	wrongReqBody := `{"email": "test@dorminet.studio", "otp": "000000"}`

	for i := 0; i < 6; i++ {
		req := httptest.NewRequest("POST", "/api/verify-otp", bytes.NewBufferString(wrongReqBody))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		handler(w, req)

		if i < 4 {
			if w.Code != http.StatusUnauthorized {
				t.Errorf("Expected 401 Unauthorized for attempt %d, got %d", i+1, w.Code)
			}
		} else {
			if w.Code != http.StatusTooManyRequests {
				t.Errorf("Expected 429 Too Many Requests for attempt %d, got %d", i+1, w.Code)
			}
		}
	}


	db.Exec("DELETE FROM auth_rate_limits")


	correctReqBody := `{"email": "test@dorminet.studio", "otp": "123456"}`
	req := httptest.NewRequest("POST", "/api/verify-otp", bytes.NewBufferString(correctReqBody))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	handler(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected 200 OK for correct OTP, got %d", w.Code)
	}


	expiredOTP := "654321"
	pastTime := time.Now().Add(-15 * time.Minute).Format(time.RFC3339)
	db.Exec("INSERT OR REPLACE INTO password_resets (email, token, expires_at) VALUES (?, ?, ?)", email, expiredOTP, pastTime)

	expiredReqBody := `{"email": "test@dorminet.studio", "otp": "654321"}`
	reqExpired := httptest.NewRequest("POST", "/api/verify-otp", bytes.NewBufferString(expiredReqBody))
	reqExpired.Header.Set("Content-Type", "application/json")
	wExpired := httptest.NewRecorder()
	handler(wExpired, reqExpired)

	if wExpired.Code != http.StatusUnauthorized {
		t.Errorf("Expected 401 Unauthorized for expired OTP, got %d", wExpired.Code)
	}

	var res map[string]string
	json.NewDecoder(wExpired.Body).Decode(&res)
	if res["error"] != "รหัส OTP หมดอายุแล้ว กรุณาขอใหม่" {
		t.Errorf("Expected expiry error message, got %v", res["error"])
	}
}
