package main

import (
	"fmt"
	"net"
	"strconv"
	"strings"
	"sync"
	"time"
)

var defaultProbePorts = []int{80, 443, 22, 8080, 8000, 3000, 53, 5230, 2283, 8096}

func scanSingleHost(ip string, ports []int, timeout time.Duration) *Device {
	start := time.Now()
	var openPorts []string

	for _, p := range ports {
		target := net.JoinHostPort(ip, strconv.Itoa(p))
		conn, err := net.DialTimeout("tcp", target, timeout)
		if err == nil {
			conn.Close()
			openPorts = append(openPorts, strconv.Itoa(p))
		}
	}

	if len(openPorts) == 0 {
		return nil
	}

	elapsed := float64(time.Since(start).Microseconds()) / 1000.0

	hostname := ""
	names, err := net.LookupAddr(ip)
	if err == nil && len(names) > 0 {
		hostname = strings.TrimSuffix(names[0], ".")
	}

	vlanTag := "Default Subnet"
	parts := strings.Split(ip, ".")
	if len(parts) >= 3 {
		vlanTag = fmt.Sprintf("VLAN / %s.%s.%s.0", parts[0], parts[1], parts[2])
	}

	return &Device{
		IP:         ip,
		Hostname:   hostname,
		SubnetVLAN: vlanTag,
		LatencyMs:  elapsed,
		Status:     "online",
		Ports:      strings.Join(openPorts, ", "),
		LastSeen:   time.Now().Format("2006-01-02 15:04:05"),
	}
}

func ScanSubnetRange(subnetPrefix string, startIP, endIP int, timeoutMs int) []Device {
	if timeoutMs <= 0 {
		timeoutMs = 150
	}
	timeout := time.Duration(timeoutMs) * time.Millisecond

	var wg sync.WaitGroup
	resultsChan := make(chan *Device, endIP-startIP+1)
	sem := make(chan struct{}, 64)

	for i := startIP; i <= endIP; i++ {
		ip := fmt.Sprintf("%s.%d", subnetPrefix, i)
		wg.Add(1)
		go func(targetIP string) {
			defer wg.Done()
			sem <- struct{}{}
			defer func() { <-sem }()

			dev := scanSingleHost(targetIP, defaultProbePorts, timeout)
			if dev != nil {
				resultsChan <- dev
			}
		}(ip)
	}

	wg.Wait()
	close(resultsChan)

	var devices []Device
	for dev := range resultsChan {
		devices = append(devices, *dev)
	}
	return devices
}

func ScanMultipleSubnets(subnets []string, timeoutMs int) []Device {
	var allDevices []Device
	for _, sub := range subnets {
		sub = strings.TrimSpace(sub)
		if sub == "" {
			continue
		}
		parts := strings.Split(sub, ".")
		var prefix string
		if len(parts) == 4 {
			prefix = fmt.Sprintf("%s.%s.%s", parts[0], parts[1], parts[2])
		} else if len(parts) == 3 {
			prefix = sub
		} else {
			continue
		}

		devs := ScanSubnetRange(prefix, 1, 254, timeoutMs)
		allDevices = append(allDevices, devs...)
	}
	return allDevices
}
