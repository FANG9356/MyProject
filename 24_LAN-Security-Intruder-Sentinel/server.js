const express = require('express');
const app = express();
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const io = new Server(server);
const { exec } = require('child_process');
const si = require('systeminformation');

app.use(express.static('public'));

const trustedMacs = [
    '20:8:89:4f:33:64',
    'f0:ee:7a:71:a9:95',
    '16:22:4b:33:bc:21'
];

function getLatency(ip) {
    return new Promise(resolve => {
        exec(`ping -c 1 -W 1000 ${ip}`, (error, stdout) => {
            if (error) return resolve(null);
            const timeMatch = stdout.match(/time=(\d+\.?\d*)/);
            resolve(timeMatch ? timeMatch[1] : null);
        });
    });
}

function checkInternet() {
    return new Promise(resolve => {
        exec('ping -c 1 -W 1000 8.8.8.8', (error, stdout) => {
            if (error) {
                resolve({ status: 'Offline', latency: 0 });
            } else {
                const timeMatch = stdout.match(/time=(\d+\.?\d*)/);
                resolve({
                    status: 'Online',
                    latency: timeMatch ? timeMatch[1] : 0
                });
            }
        });
    });
}

async function scanNetwork() {
    return new Promise((resolve) => {
        exec('arp -a', async (error, stdout) => {
            if (error) return resolve([]);
            const rawLines = stdout.split('\n').filter(line => line.includes('at'));
            const devices = [];
            for (const line of rawLines) {
                const parts = line.match(/\((.*?)\) at (.*?) on (.*?)/);
                if (parts) {
                    const ip = parts[1];
                    const mac = parts[2];
                    if (!ip.startsWith('224') && !ip.startsWith('255')) {
                        const latency = await getLatency(ip);
                        if (latency !== null) {
                            const isTrusted = trustedMacs.some(trusted => mac.includes(trusted) || trusted.includes(mac));
                            devices.push({
                                ip,
                                mac,
                                latency,
                                isTrusted
                            });
                        }
                    }
                }
            }
            resolve(devices);
        });
    });
}

function formatUptime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return `${h}h ${m}m`;
}

io.on('connection', (socket) => {
    const interval = setInterval(async () => {
        try {
            const netStats = await si.networkStats();
            const mainIfName = await si.networkInterfaceDefault();
            const mainIfStat = netStats.find(i => i.iface === mainIfName) || netStats[0];

            const interfaces = await si.networkInterfaces();
            const myInterface = interfaces.find(i => i.iface === mainIfName);
            const myIp = myInterface ? myInterface.ip4 : 'Unknown';

            const cpu = await si.currentLoad();
            const mem = await si.mem();
            const time = si.time();

            const fsSize = await si.fsSize();
            let mainDisk = fsSize.find(d => d.mount === '/System/Volumes/Data') || fsSize[0] || { use: 0, size: 0 };

            const internet = await checkInternet();
            const devices = await scanNetwork();

            socket.emit('dashboard-update', {
                hostIp: myIp,
                hostSpeed: {
                    download: (mainIfStat.rx_sec / 1024 / 1024 * 8).toFixed(2),
                    upload: (mainIfStat.tx_sec / 1024 / 1024 * 8).toFixed(2)
                },
                system: {
                    cpu: cpu.currentLoad.toFixed(1),
                    ram: (mem.active / mem.total * 100).toFixed(1),
                    uptime: formatUptime(time.uptime),
                    diskPercent: mainDisk.use.toFixed(1),
                    diskTotal: (mainDisk.size / 1024 / 1024 / 1024).toFixed(0)
                },
                internet: internet,
                devices: devices
            });
        } catch (e) {}
    }, 5000);

    socket.on('disconnect', () => { clearInterval(interval); });
});

const PORT = process.env.PORT || 3080;
server.listen(PORT, () => {
    console.log(`Security Sentinel running at http://localhost:${PORT}`);
});

module.exports = { app, server, checkInternet, scanNetwork, trustedMacs };
