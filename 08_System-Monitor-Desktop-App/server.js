const express = require('express');
const app = express();
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const io = new Server(server);
const si = require('systeminformation');
const path = require('path');
const { exec } = require('child_process'); // เรียกใช้คำสั่งเครื่องโดยตรง

// --- ตั้งค่า path ---
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// --- ฟังก์ชันเปิด Browser (เขียนเอง ไม่ง้อ library) ---
function openBrowser(url) {
    let command;
    // เช็คว่าเป็น Windows หรือ Mac แล้วเลือกคำสั่งให้ถูก
    if (process.platform === 'win32') {
        command = `start "" "${url}"`; // คำสั่ง Windows
    } else if (process.platform === 'darwin') {
        command = `open "${url}"`;     // คำสั่ง Mac
    } else {
        command = `xdg-open "${url}"`; // คำสั่ง Linux
    }
    
    exec(command, (err) => {
        if (err) console.log("Auto-open browser failed (it's okay, just open manually).");
    });
}

// --- ฟังก์ชัน Ping ---
function getLatency(ip) {
    return new Promise(resolve => {
        const cmd = process.platform === 'win32' ? `ping -n 1 -w 1000 ${ip}` : `ping -c 1 -W 1 ${ip}`;
        exec(cmd, (error, stdout) => {
            if (error) return resolve('-');
            const timeMatch = stdout.match(/time[=<](\d+\.?\d*)ms?/);
            resolve(timeMatch ? timeMatch[1] + 'ms' : '-');
        });
    });
}

// --- การทำงานหลัก ---
io.on('connection', (socket) => {
    let clientIp = socket.handshake.headers['x-forwarded-for'] || socket.handshake.address;
    if (clientIp.startsWith("::ffff:")) clientIp = clientIp.substr(7);
    socket.emit('your-ip', clientIp);

    const sendUpdate = async () => {
        try {
            const cpu = await si.currentLoad();
            const mem = await si.mem();
            const osInfo = await si.osInfo();
            
            socket.emit('dashboard-update', {
                os: `${osInfo.distro} ${osInfo.release}`,
                cpu: cpu.currentLoad.toFixed(1),
                ram: (mem.active / mem.total * 100).toFixed(1),
                ramTotal: (mem.total / 1024 / 1024 / 1024).toFixed(1)
            });
        } catch (e) {
            console.error('System info fetch error:', e);
        }
    };

    sendUpdate(); // Send immediate initial stats
    const interval = setInterval(sendUpdate, 3000);

    socket.on('disconnect', () => { clearInterval(interval); });
});

// --- เริ่มรัน Server ---
const PORT = 3000;
server.listen(PORT, () => {
    console.log(`🚀 System Monitor Station Started on Port ${PORT}`);
    // เรียกใช้ฟังก์ชันเปิด Browser ของเราเอง
    if (!process.env.HEADLESS) {
        openBrowser(`http://localhost:${PORT}`);
    }
});