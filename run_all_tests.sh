#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
echo "================================================================================"
echo "EXECUTING AUTOMATED TEST SUITE FOR ALL 25 PROJECTS"
echo "================================================================================"

pass_count=0

run_test() {
    local num="$1"
    local title="$2"
    local cmd="$3"
    local cwd="$4"
    
    echo ""
    echo "[Running Test $num] $title..."
    cd "$cwd"
    if eval "$cmd"; then
        echo "   -> Result: PASS"
        pass_count=$((pass_count + 1))
    else
        echo "   -> Result: FAIL"
    fi
}

run_test "01" "AI Wi-Fi Sensing & Activity Recognition" \
    "\"/Volumes/FangB/wifiwall/venv/bin/python3\" test_simulation.py" \
    "$DIR/01_AI-WiFi-Sensing-Wall"

run_test "02" "Smart Doc AI Academic Research Generator" \
    "\"/Volumes/FangB/smart-doc-ai/venv/bin/python3\" test_simulation.py" \
    "$DIR/02_Smart-Doc-AI"

run_test "03" "Tip Desk PromptPay Real-time System" \
    "\"/Volumes/FangB/tip/.venv/bin/python3\" test_simulation.py" \
    "$DIR/03_Tip-Desk-PromptPay"

run_test "04" "Club Management System & Attendance" \
    "node test_simulation.js" \
    "$DIR/04_Club-Management-System"

run_test "05" "ATM Security & YOLOv8 Person Detector" \
    "\"/Volumes/FangB/atm/venv/bin/python3\" test_simulation.py" \
    "$DIR/05_ATM-YOLOv8-Detector"

run_test "06" "Smart Karaoke Streaming & Mobile Remote" \
    "\"/Volumes/FangB/tip/.venv/bin/python3\" test_simulation.py" \
    "$DIR/06_Karaoke-Streaming-System"

run_test "07" "AdGuard Time Portal & Quota Control" \
    "node test_simulation.js" \
    "$DIR/07_AdGuard-Time-Portal"

run_test "08" "System Monitor Desktop Application" \
    "node test_simulation.js" \
    "$DIR/08_System-Monitor-Desktop-App"

run_test "09" "Home Server Infrastructure & Docker Stack" \
    "\"/Volumes/FangB/atm/venv/bin/python3\" test_simulation.py" \
    "$DIR/09_HomeServer-Infrastructure"

run_test "10" "Music Shuffle AI Voice Desktop Player" \
    "\"/Volumes/FangB/tip/.venv/bin/python3\" test_simulation.py" \
    "$DIR/10_Music-Shuffle-AI"

run_test "11" "Bottle & Can Automated Sorter" \
    "python3 test_simulation.py" \
    "$DIR/11_Bottle-Can-Sorter"

run_test "12" "Smart Plant Watering Remote System" \
    "python3 test_simulation.py" \
    "$DIR/12_Smart-Plant-Watering"

run_test "13" "General Education Web Portal" \
    "python3 test_simulation.py" \
    "$DIR/13_General-Education-Web"

run_test "14" "Computer Fundamentals Quiz System" \
    "python3 test_simulation.py" \
    "$DIR/14_Computer-Quiz-System"

run_test "15" "SD Calculator & Statistics App" \
    "python3 test_simulation.py" \
    "$DIR/15_SD-Calculator-Python"

run_test "16" "Duplicate File Cleaner Utility" \
    "python3 test_simulation.py" \
    "$DIR/16_Duplicate-File-Cleaner"

run_test "17" "GPA & GPAX Academic Grade Calculator" \
    "python3 test_simulation.py" \
    "$DIR/17_Grade-Calculator-Python"

run_test "18" "Neo Web Chat & Offline BLE Mesh" \
    "python3 test_simulation.py" \
    "$DIR/18_Neo-Web-Chat"

run_test "19" "DevOps Competition Platform 2568" \
    "node test_simulation.js" \
    "$DIR/19_DevOps-Competition-Platform"

run_test "20" "Color Detection & Kalman Filter YOLO" \
    "\"/Volumes/FangB/atm/venv/bin/python3\" test_simulation.py" \
    "$DIR/20_Color-Detection-Kalman-YOLO"

run_test "21" "Autonomous Robot Moisture Tracker" \
    "node test_simulation.js" \
    "$DIR/21_Robot-Moisture-Tracker"

run_test "22" "PDF Speech Synthesizer & Audio Reader" \
    "\"/Volumes/FangB/tip/.venv/bin/python3\" test_simulation.py" \
    "$DIR/22_PDF-Speech-Synthesizer"

run_test "23" "Discord Voice & Screen Sharing Clone" \
    "python3 test_simulation.py" \
    "$DIR/23_Discord-Voice-Screen-Share"

run_test "24" "LAN Security Intruder Sentinel" \
    "node test_simulation.js" \
    "$DIR/24_LAN-Security-Intruder-Sentinel"

run_test "25" "DormiNetX Windows Desktop Standalone" \
    "node test_simulation.js" \
    "$DIR/25_DormiNetX-Windows-Desktop"

echo ""
echo "================================================================================"
echo "FINAL TEST REPORT: $pass_count / 25 PROJECTS PASSED ALL TESTS SUCCESSFULLY"
echo "================================================================================"
