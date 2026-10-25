package main

import (
	"context"
	"fmt"
	"net"
	"strings"
	"sync"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"dorm_os/core"
)

type App struct {
	ctx         context.Context
	serverOnce  sync.Once
}

func NewApp() *App {
	return &App{}
}

func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
	
}

func (a *App) Greet(name string) string {
	return fmt.Sprintf("Hello %s, It's show time!", name)
}

func (a *App) StartLocalServer() string {
	os.WriteFile("debug_start_server.txt", []byte("StartLocalServer called!"), 0644)
	a.serverOnce.Do(func() {
		os.WriteFile("debug_start_server_do.txt", []byte("Inside serverOnce!"), 0644)
		go core.RunServer()
	})
	return "ok"
}

func (a *App) GetLocalIP() string {
	conn, err := net.Dial("udp", "8.8.8.8:80")
	if err != nil {
		return "127.0.0.1"
	}
	defer conn.Close()
	localAddr := conn.LocalAddr().(*net.UDPAddr)
	return localAddr.IP.String()
}

func (a *App) GetLocalSubnet() string {
	ip := a.GetLocalIP()
	parts := strings.Split(ip, ".")
	if len(parts) == 4 {
		return fmt.Sprintf("%s.%s.%s", parts[0], parts[1], parts[2])
	}
	return "192.168.1"
}

func (a *App) PrintHtml(html string) string {
	
	if !strings.Contains(strings.ToLower(html), "charset=\"utf-8\"") && !strings.Contains(strings.ToLower(html), "charset='utf-8'") && !strings.Contains(strings.ToLower(html), "charset=utf-8") {
		html = strings.Replace(html, "<head>", "<head>\n<meta charset=\"UTF-8\">\n", 1)
	}

	script := `<script>window.onload = function() { setTimeout(function(){ window.print(); }, 500); }</script>`
	if !strings.Contains(html, "window.print") {
		html = strings.Replace(html, "</body>", script+"\n</body>", 1)
	}

	tmpDir := os.TempDir()
	filePath := filepath.Join(tmpDir, "dorminet_receipt.html")
	err := os.WriteFile(filePath, []byte(html), 0644)
	if err != nil {
		return err.Error()
	}

	var cmd *exec.Cmd
	switch runtime.GOOS {
	case "windows":
		cmd = exec.Command("cmd", "/c", "start", filePath)
	case "darwin":
		cmd = exec.Command("open", filePath)
	default: 
		cmd = exec.Command("xdg-open", filePath)
	}

	err = cmd.Start()
	if err != nil {
		return err.Error()
	}
	return "ok"
}
