package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

var db *sql.DB

func enableCORS(w http.ResponseWriter, r *http.Request) bool {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
	if r.Method == http.MethodOptions {
		w.WriteHeader(http.StatusOK)
		return true
	}
	return false
}

func handleServices(w http.ResponseWriter, r *http.Request) {
	if enableCORS(w, r) {
		return
	}

	if r.Method == http.MethodGet {
		rows, err := db.Query("SELECT id, name, category, url, icon, description, status, latency_ms, last_check FROM services ORDER BY category, name")
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		defer rows.Close()

		var services []Service
		for rows.Next() {
			var s Service
			if err := rows.Scan(&s.ID, &s.Name, &s.Category, &s.URL, &s.Icon, &s.Description, &s.Status, &s.LatencyMs, &s.LastCheck); err == nil {
				services = append(services, s)
			}
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(services)
		return
	}

	if r.Method == http.MethodPost {
		var s Service
		if err := json.NewDecoder(r.Body).Decode(&s); err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}

		stmt, err := db.Prepare("INSERT INTO services (name, category, url, icon, description, status) VALUES (?, ?, ?, ?, ?, 'online')")
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		defer stmt.Close()

		res, err := stmt.Exec(s.Name, s.Category, s.URL, s.Icon, s.Description)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		id, _ := res.LastInsertId()
		s.ID = int(id)
		s.Status = "online"
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(s)
		return
	}

	http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
}

func handleServicesHealth(w http.ResponseWriter, r *http.Request) {
	if enableCORS(w, r) {
		return
	}

	rows, err := db.Query("SELECT id, url FROM services")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	type target struct {
		id  int
		url string
	}
	var targets []target
	for rows.Next() {
		var t target
		if err := rows.Scan(&t.id, &t.url); err == nil {
			targets = append(targets, t)
		}
	}

	for _, t := range targets {
		status := "offline"
		latency := 0.0

		u, err := url.Parse(t.url)
		host := t.url
		port := "80"
		if err == nil && u.Host != "" {
			host = u.Host
		}
		if !strings.Contains(host, ":") {
			host = net.JoinHostPort(host, port)
		}

		start := time.Now()
		conn, err := net.DialTimeout("tcp", host, 350*time.Millisecond)
		if err == nil {
			conn.Close()
			status = "online"
			latency = float64(time.Since(start).Microseconds()) / 1000.0
		}

		db.Exec("UPDATE services SET status = ?, latency_ms = ?, last_check = CURRENT_TIMESTAMP WHERE id = ?", status, latency, t.id)
	}

	handleServices(w, r)
}

func handleDevices(w http.ResponseWriter, r *http.Request) {
	if enableCORS(w, r) {
		return
	}

	rows, err := db.Query("SELECT id, ip, hostname, subnet_vlan, latency_ms, status, ports, last_seen FROM devices ORDER BY ip")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var devices []Device
	for rows.Next() {
		var d Device
		if err := rows.Scan(&d.ID, &d.IP, &d.Hostname, &d.SubnetVLAN, &d.LatencyMs, &d.Status, &d.Ports, &d.LastSeen); err == nil {
			devices = append(devices, d)
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(devices)
}

func handleScan(w http.ResponseWriter, r *http.Request) {
	if enableCORS(w, r) {
		return
	}

	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Subnets   []string `json:"subnets"`
		TimeoutMs int      `json:"timeout_ms"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || len(req.Subnets) == 0 {
		req.Subnets = []string{"192.168.1", "10.0.0"}
	}
	if req.TimeoutMs <= 0 {
		req.TimeoutMs = 150
	}

	found := ScanMultipleSubnets(req.Subnets, req.TimeoutMs)

	stmt, err := db.Prepare(`
		INSERT INTO devices (ip, hostname, subnet_vlan, latency_ms, status, ports, last_seen)
		VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
		ON CONFLICT(ip) DO UPDATE SET
			hostname = excluded.hostname,
			subnet_vlan = excluded.subnet_vlan,
			latency_ms = excluded.latency_ms,
			status = excluded.status,
			ports = excluded.ports,
			last_seen = CURRENT_TIMESTAMP
	`)
	if err == nil {
		defer stmt.Close()
		for _, d := range found {
			stmt.Exec(d.IP, d.Hostname, d.SubnetVLAN, d.LatencyMs, d.Status, d.Ports)
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"scanned_subnets": req.Subnets,
		"total_found":     len(found),
		"devices":         found,
	})
}

func handleStats(w http.ResponseWriter, r *http.Request) {
	if enableCORS(w, r) {
		return
	}

	var totalServices, onlineServices, totalDevices int
	db.QueryRow("SELECT COUNT(*) FROM services").Scan(&totalServices)
	db.QueryRow("SELECT COUNT(*) FROM services WHERE status = 'online'").Scan(&onlineServices)
	db.QueryRow("SELECT COUNT(*) FROM devices").Scan(&totalDevices)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"total_services":  totalServices,
		"online_services": onlineServices,
		"total_devices":   totalDevices,
		"system_status":   "operational",
		"engine":          "Go High-Concurrency Goroutine Core",
		"database":        "SQLite3 Embedded",
	})
}

func main() {
	dbPath := "infrastructure.db"
	if custom := os.Getenv("DB_PATH"); custom != "" {
		dbPath = custom
	}

	var err error
	db, err = initDB(dbPath)
	if err != nil {
		fmt.Printf("Database initialization failed: %v\n", err)
		os.Exit(1)
	}
	defer db.Close()

	http.HandleFunc("/api/services", handleServices)
	http.HandleFunc("/api/services/health", handleServicesHealth)
	http.HandleFunc("/api/devices", handleDevices)
	http.HandleFunc("/api/scan", handleScan)
	http.HandleFunc("/api/stats", handleStats)

	distCandidates := []string{"../frontend/dist", "frontend/dist", "./dist"}
	var distDir string
	for _, c := range distCandidates {
		if _, err := os.Stat(c); err == nil {
			distDir = c
			break
		}
	}

	if distDir != "" {
		fs := http.FileServer(http.Dir(distDir))
		http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
			path := filepath.Join(distDir, r.URL.Path)
			if _, err := os.Stat(path); os.IsNotExist(err) {
				http.ServeFile(w, r, filepath.Join(distDir, "index.html"))
				return
			}
			fs.ServeHTTP(w, r)
		})
	}

	port := 8001
	if p := os.Getenv("PORT"); p != "" {
		if val, err := strconv.Atoi(p); err == nil {
			port = val
		}
	}

	fmt.Printf("HomeServer Infrastructure Engine active on port %d\n", port)
	if err := http.ListenAndServe(fmt.Sprintf(":%d", port), nil); err != nil {
		fmt.Printf("Server halted: %v\n", err)
	}
}
