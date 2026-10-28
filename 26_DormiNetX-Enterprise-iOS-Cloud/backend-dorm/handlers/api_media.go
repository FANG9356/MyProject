package handlers

import (
	"crypto/hmac"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

const lineMediaURLLifetime = 24 * time.Hour


func SignedLineMediaURL(baseURL, storedPath string, now time.Time) (string, error) {
	fileName := mediaFileName(storedPath)
	if fileName == "" {
		return "", fmt.Errorf("invalid media path")
	}
	baseURL = strings.TrimRight(strings.TrimSpace(baseURL), "/")
	if baseURL == "" {
		return "", fmt.Errorf("missing public base URL")
	}
	expires := now.Add(lineMediaURLLifetime).Unix()
	signature := signLineMedia(fileName, expires)
	return fmt.Sprintf("%s/line-media/%s?expires=%d&sig=%s", baseURL, url.PathEscape(fileName), expires, signature), nil
}

func signLineMedia(fileName string, expires int64) string {
	mac := hmac.New(sha256.New, getJWTSecret())
	_, _ = fmt.Fprintf(mac, "dorminet-line-media-v1\n%s\n%d", fileName, expires)
	return hex.EncodeToString(mac.Sum(nil))
}

func mediaFileName(storedPath string) string {
	cleaned := strings.TrimSpace(strings.ReplaceAll(storedPath, "\\", "/"))
	cleaned = strings.TrimPrefix(cleaned, "/uploads/")
	cleaned = strings.TrimPrefix(cleaned, "uploads/")
	if cleaned == "" || cleaned == "." || filepath.Base(cleaned) != cleaned {
		return ""
	}
	return cleaned
}


func HandleSignedLineMedia() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet && r.Method != http.MethodHead {
			http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
			return
		}
		fileName := mediaFileName(strings.TrimPrefix(r.URL.Path, "/line-media/"))
		expires, err := strconv.ParseInt(r.URL.Query().Get("expires"), 10, 64)
		providedSignature, decodeErr := hex.DecodeString(r.URL.Query().Get("sig"))
		expectedSignature, expectedDecodeErr := hex.DecodeString(signLineMedia(fileName, expires))
		if fileName == "" || err != nil || decodeErr != nil || expectedDecodeErr != nil ||
			time.Now().Unix() > expires || !hmac.Equal(providedSignature, expectedSignature) {
			http.Error(w, "Media not found", http.StatusNotFound)
			return
		}
		servePrivateUpload(w, r, fileName, "public, max-age=300")
	}
}


func HandleLegacyPublicUploadsDisabled(w http.ResponseWriter, r *http.Request) {
	http.Error(w, "Media not found", http.StatusNotFound)
}


func HandleTenantMedia(master *sql.DB) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
			return
		}
		fileName := mediaFileName(strings.TrimPrefix(r.URL.Path, "/api/media/"))
		if fileName == "" {
			http.Error(w, "Invalid media path", http.StatusBadRequest)
			return
		}
		tenantDB, err := RequestTenantDB(r, master)
		if err != nil {
			http.Error(w, "Tenant unavailable", http.StatusForbidden)
			return
		}
		allowed, err := tenantReferencesMedia(tenantDB, fileName)
		if err != nil {
			http.Error(w, "Media lookup failed", http.StatusInternalServerError)
			return
		}
		if !allowed {
			http.Error(w, "Media not found", http.StatusNotFound)
			return
		}
		servePrivateUpload(w, r, fileName, "private, max-age=300")
	}
}

func servePrivateUpload(w http.ResponseWriter, r *http.Request, fileName, cacheControl string) {
	file, err := os.Open(filepath.Join("uploads", fileName))
	if err != nil {
		http.Error(w, "Media not found", http.StatusNotFound)
		return
	}
	defer file.Close()
	info, err := file.Stat()
	if err != nil || !info.Mode().IsRegular() {
		http.Error(w, "Media not found", http.StatusNotFound)
		return
	}
	digest := sha256.New()
	if _, err := io.Copy(digest, file); err != nil {
		http.Error(w, "Media unavailable", http.StatusInternalServerError)
		return
	}
	if _, err := file.Seek(0, io.SeekStart); err != nil {
		http.Error(w, "Media unavailable", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Cache-Control", cacheControl)
	w.Header().Set("X-Content-SHA256", hex.EncodeToString(digest.Sum(nil)))
	w.Header().Set("X-Content-Type-Options", "nosniff")
	http.ServeContent(w, r, fileName, info.ModTime(), file)
}

func tenantReferencesMedia(db *sql.DB, fileName string) (bool, error) {
	withUploadPrefix := "/uploads/" + fileName
	var allowed bool
	err := db.QueryRow(`SELECT EXISTS(
		SELECT 1 FROM payments p
		WHERE p.slip_path IN (?, ?)
		   OR EXISTS (SELECT 1 FROM json_each(CASE WHEN json_valid(p.slip_path_array) THEN p.slip_path_array ELSE '[]' END)
		              WHERE value IN (?, ?))
		UNION ALL
		SELECT 1 FROM maintenances m
		WHERE m.slip_path IN (?, ?)
		   OR instr(',' || REPLACE(COALESCE(m.issue_image, ''), '/uploads/', '') || ',', ',' || ? || ',') > 0
		UNION ALL
		SELECT 1 FROM users u
		WHERE EXISTS (SELECT 1 FROM json_each(CASE WHEN json_valid(u.booking_slips) THEN u.booking_slips ELSE '[]' END)
		              WHERE value IN (?, ?))
		UNION ALL
		SELECT 1 FROM room_conditions c
		WHERE c.image_path IN (?, ?)
	)`, fileName, withUploadPrefix, fileName, withUploadPrefix,
		fileName, withUploadPrefix, fileName, fileName, withUploadPrefix,
		fileName, withUploadPrefix).Scan(&allowed)
	return allowed, err
}
