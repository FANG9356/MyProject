#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
echo "================================================================================"
echo "🚀 EXECUTING COMPREHENSIVE AUTOMATED TEST SUITE FOR ALL 9 PROJECTS"
echo "================================================================================"

pass_count=0

run_test() {
    local num="$1"
    local title="$2"
    local cmd="$3"
    local cwd="$4"
    
    echo ""
    echo "▶️ [Running Test $num] $title..."
    cd "$cwd"
    if eval "$cmd"; then
        echo "   -> Result: PASS ✅"
        pass_count=$((pass_count + 1))
    else
        echo "   -> Result: FAIL ❌"
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

run_test "06" "Fang Karaoke Streaming & Mobile Remote" \
    ""/Volumes/FangB/tip/.venv/bin/python3" test_simulation.py" \
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

echo ""
echo "================================================================================"
echo "🎯 FINAL TEST REPORT: $pass_count / 9 PROJECTS PASSED ALL TESTS SUCCESSFULLY!"
echo "================================================================================"
