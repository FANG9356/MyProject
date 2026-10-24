require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const schedule = require('node-schedule');
const db = require('./database');
const { blockInternet, unblockInternet } = require('./adguard');

const app = express();
const PORT = process.env.PORT || 8080;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Generate a random 6-digit PIN
function generateRandomPin() {
    return Math.floor(100000 + Math.random() * 900000).toString();
}

// Ensure PIN is unique
function generateUniquePin(callback) {
    const pin = generateRandomPin();
    db.get('SELECT id FROM pins WHERE pin = ?', [pin], (err, row) => {
        if (err) return callback(err);
        if (row) return generateUniquePin(callback); // collision, try again
        callback(null, pin);
    });
}

// API: Generate PINs
app.post('/api/generate', (req, res) => {
    const { count = 1, duration_hours = 1 } = req.body;
    let generated = 0;
    let pins = [];
    
    const generateNext = () => {
        if (generated >= count) {
            return res.json({ success: true, pins });
        }
        generateUniquePin((err, pin) => {
            if (err) return res.status(500).json({ error: 'Database error' });
            db.run('INSERT INTO pins (pin, duration_hours) VALUES (?, ?)', [pin, duration_hours], function(err) {
                if (err) return res.status(500).json({ error: 'Database error' });
                pins.push({ pin, duration_hours });
                generated++;
                generateNext();
            });
        });
    };
    generateNext();
});

// API: Unlock Internet
app.post('/api/unlock', (req, res) => {
    const { pin } = req.body;
    if (!pin) return res.status(400).json({ error: 'PIN is required' });

    db.get('SELECT * FROM pins WHERE pin = ?', [pin], (err, row) => {
        if (err) return res.status(500).json({ error: 'Database error' });
        if (!row) return res.status(404).json({ error: 'รหัส PIN ไม่ถูกต้อง' });
        if (row.is_used) return res.status(400).json({ error: 'รหัส PIN นี้ถูกใช้งานไปแล้ว' });

        const now = Date.now();
        const expires_at = now + (row.duration_hours * 60 * 60 * 1000);

        db.run('UPDATE pins SET is_used = 1, used_at = ?, expires_at = ? WHERE id = ?', 
            [now, expires_at, row.id], 
            async (err) => {
                if (err) return res.status(500).json({ error: 'Database error' });
                
                await unblockInternet();
                res.json({ success: true, message: 'ปลดล็อกอินเทอร์เน็ตสำเร็จ!', expires_at });
            }
        );
});
});

// API: Revoke active session
app.post('/api/revoke', (req, res) => {
    const { pin } = req.body;
    if (!pin) return res.status(400).json({ error: 'PIN is required' });

    db.get('SELECT * FROM pins WHERE pin = ? AND is_used = 1 AND expires_at > ?', [pin, Date.now()], (err, row) => {
        if (err) return res.status(500).json({ error: 'Database error' });
        if (!row) return res.status(404).json({ error: 'ไม่พบรหัสที่กำลังใช้งานอยู่' });

        // Set expires_at to now to invalidate it
        db.run('UPDATE pins SET expires_at = ? WHERE id = ?', [Date.now(), row.id], async (err) => {
            if (err) return res.status(500).json({ error: 'Database error' });
            
            await blockInternet();
            res.json({ success: true, message: 'ยกเลิกรหัสสำเร็จและตัดเน็ตแล้ว!' });
        });
    });
});

// API: Check active session
app.get('/api/status', (req, res) => {
    const now = Date.now();
    db.get('SELECT pin, expires_at FROM pins WHERE is_used = 1 AND expires_at > ? ORDER BY expires_at DESC LIMIT 1', [now], (err, row) => {
        if (err) return res.status(500).json({ error: 'Database error' });
        if (row) {
            res.json({ active: true, expires_at: row.expires_at, pin: row.pin });
        } else {
            res.json({ active: false });
        }
    });
});

// API: Get all pins (for admin)
app.get('/api/pins', (req, res) => {
    db.all('SELECT * FROM pins ORDER BY id DESC LIMIT 100', (err, rows) => {
        if (err) return res.status(500).json({ error: 'Database error' });
        res.json({ pins: rows });
    });
});

// API: Delete a pin
app.delete('/api/pins/:id', (req, res) => {
    const id = req.params.id;
    db.run('DELETE FROM pins WHERE id = ?', [id], (err) => {
        if (err) return res.status(500).json({ error: 'Database error' });
        res.json({ success: true });
    });
});

// Cron job to check for expiration every 1 minute
schedule.scheduleJob('* * * * *', () => {
    const now = Date.now();
    
    // Auto-delete pins that expired more than 5 minutes ago
    const fiveMinsAgo = now - (5 * 60 * 1000);
    db.run('DELETE FROM pins WHERE is_used = 1 AND expires_at <= ?', [fiveMinsAgo], (err) => {
        if (err) console.error('Error auto-deleting pins:', err);
    });

    db.get('SELECT id FROM pins WHERE is_used = 1 AND expires_at > ?', [now], async (err, row) => {
        if (err) return console.error('Cron DB error:', err);
        if (!row) {
            // No active session. Ensure blocked.
            await blockInternet();
        }
    });

    // Auto-maintain 3 unused pins at all times
    db.get('SELECT count(*) as count FROM pins WHERE is_used = 0', [], (err, unRow) => {
        if (!err && unRow) {
            const needed = 3 - unRow.count;
            if (needed > 0) {
                db.get('SELECT duration_hours FROM pins ORDER BY id DESC LIMIT 1', [], (err, lastPin) => {
                    const duration = (lastPin && lastPin.duration_hours) ? lastPin.duration_hours : 1;
                    for (let i = 0; i < needed; i++) {
                        generateUniquePin((err, pin) => {
                            if (!err) {
                                db.run('INSERT INTO pins (pin, duration_hours) VALUES (?, ?)', [pin, duration]);
                                console.log(`[Auto-Generate] Created new PIN: ${pin} for ${duration} hours`);
                            }
                        });
                    }
                });
            }
        }
    });
});


// Initialize block on startup if no active session
setTimeout(() => {
    const now = Date.now();
    db.get('SELECT id FROM pins WHERE is_used = 1 AND expires_at > ?', [now], async (err, row) => {
        if (!row) {
            console.log('[Startup] No active session found. Blocking internet...');
            await blockInternet();
        } else {
            console.log('[Startup] Active session found. Ensuring internet is unblocked...');
            await unblockInternet();
        }
    });
}, 2000);

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
