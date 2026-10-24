package main

import (
	"database/sql"
	_ "github.com/mattn/go-sqlite3"
)

type Service struct {
	ID          int     `json:"id"`
	Name        string  `json:"name"`
	Category    string  `json:"category"`
	URL         string  `json:"url"`
	Icon        string  `json:"icon"`
	Description string  `json:"description"`
	Status      string  `json:"status"`
	LatencyMs   float64 `json:"latency_ms"`
	LastCheck   string  `json:"last_check"`
}

type Device struct {
	ID         int     `json:"id"`
	IP         string  `json:"ip"`
	Hostname   string  `json:"hostname"`
	SubnetVLAN string  `json:"subnet_vlan"`
	LatencyMs  float64 `json:"latency_ms"`
	Status     string  `json:"status"`
	Ports      string  `json:"ports"`
	LastSeen   string  `json:"last_seen"`
}

func initDB(filepath string) (*sql.DB, error) {
	db, err := sql.Open("sqlite3", filepath)
	if err != nil {
		return nil, err
	}

	createServicesTable := `
	CREATE TABLE IF NOT EXISTS services (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL,
		category TEXT NOT NULL,
		url TEXT NOT NULL,
		icon TEXT,
		description TEXT,
		status TEXT DEFAULT 'unknown',
		latency_ms REAL DEFAULT 0,
		last_check DATETIME DEFAULT CURRENT_TIMESTAMP
	);`

	createDevicesTable := `
	CREATE TABLE IF NOT EXISTS devices (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		ip TEXT UNIQUE NOT NULL,
		hostname TEXT,
		subnet_vlan TEXT,
		latency_ms REAL DEFAULT 0,
		status TEXT DEFAULT 'online',
		ports TEXT,
		last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
	);`

	if _, err := db.Exec(createServicesTable); err != nil {
		return nil, err
	}
	if _, err := db.Exec(createDevicesTable); err != nil {
		return nil, err
	}

	seedDefaultServices(db)
	seedDefaultDevices(db)
	return db, nil
}

func seedDefaultServices(db *sql.DB) {
	var count int
	row := db.QueryRow("SELECT COUNT(*) FROM services")
	if err := row.Scan(&count); err != nil || count > 0 {
		return
	}

	defaults := []Service{
		{Name: "Immich Photos", Category: "Media Storage", URL: "http://homeserver.local:2283", Icon: "image", Description: "Self-hosted high performance photo & video backup"},
		{Name: "Jellyfin Streaming", Category: "Media Storage", URL: "http://homeserver.local:8096", Icon: "tv", Description: "Media system for movies, series and music"},
		{Name: "FileBrowser Cloud", Category: "File Management", URL: "http://homeserver.local:8002", Icon: "folder", Description: "Web-based file manager for server storage"},
		{Name: "Bitwarden Vault", Category: "Security", URL: "https://vault.homeserver.local", Icon: "shield", Description: "End-to-end encrypted password and credential vault"},
		{Name: "Memos Knowledge", Category: "Productivity", URL: "http://homeserver.local:5230", Icon: "edit", Description: "Lightweight privacy-first note-taking service"},
		{Name: "Interactive Whiteboard", Category: "Productivity", URL: "http://homeserver.local:8081", Icon: "layout", Description: "Real-time collaborative diagramming and sketch canvas"},
		{Name: "Minecraft Server", Category: "Entertainment", URL: "homeserver.local:25565", Icon: "server", Description: "Multiplayer gaming environment with automated backups"},
	}

	stmt, err := db.Prepare("INSERT INTO services (name, category, url, icon, description, status) VALUES (?, ?, ?, ?, ?, 'online')")
	if err != nil {
		return
	}
	defer stmt.Close()

	for _, s := range defaults {
		stmt.Exec(s.Name, s.Category, s.URL, s.Icon, s.Description)
	}
}

func seedDefaultDevices(db *sql.DB) {
	var count int
	row := db.QueryRow("SELECT COUNT(*) FROM devices")
	if err := row.Scan(&count); err != nil || count > 0 {
		return
	}

	defaults := []Device{
		{IP: "192.168.1.1", Hostname: "gateway.router.local", SubnetVLAN: "VLAN 1 - Management", LatencyMs: 0.8, Ports: "80, 443, 22, 53"},
		{IP: "192.168.1.2", Hostname: "core-switch.infra", SubnetVLAN: "VLAN 1 - Management", LatencyMs: 1.1, Ports: "22, 80"},
		{IP: "192.168.10.15", Hostname: "truenas-storage.local", SubnetVLAN: "VLAN 10 - Storage", LatencyMs: 2.3, Ports: "80, 443, 22, 445"},
		{IP: "192.168.10.42", Hostname: "proxmox-cluster-node1", SubnetVLAN: "VLAN 10 - Compute", LatencyMs: 1.9, Ports: "8006, 22"},
		{IP: "10.0.0.5", Hostname: "pihole-dns-primary", SubnetVLAN: "VLAN 20 - Core Services", LatencyMs: 0.6, Ports: "53, 80"},
		{IP: "10.0.0.88", Hostname: "iot-controller-hub", SubnetVLAN: "VLAN 30 - IoT Isolated", LatencyMs: 3.4, Ports: "80, 1883"},
	}

	stmt, err := db.Prepare("INSERT INTO devices (ip, hostname, subnet_vlan, latency_ms, status, ports) VALUES (?, ?, ?, ?, 'online', ?)")
	if err != nil {
		return
	}
	defer stmt.Close()

	for _, d := range defaults {
		stmt.Exec(d.IP, d.Hostname, d.SubnetVLAN, d.LatencyMs, d.Ports)
	}
}
