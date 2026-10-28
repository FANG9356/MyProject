require('dotenv').config();
const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');
const jwt = require('jsonwebtoken');
const JWT_SECRET = process.env.JWT_SECRET || 'club_management_super_secret_key_2026';

function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    if (token == null) return res.status(401).json({ error: 'Unauthorized' });
    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) return res.status(403).json({ error: 'Forbidden' });
        req.user = user;
        next();
    });
}

const app = express();
const PORT = process.env.PORT || 3000;
const DB_PATH = process.env.DB_PATH || './database.sqlite';

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend')));

const db = new sqlite3.Database(DB_PATH, (err) => {
    if (err) {
        console.error('Error connecting to database:', err.message);
    } else {
        console.log('Connected to the SQLite database.');
        initDb();
    }
});

function initDb() {
    db.serialize(() => {
        db.run(`CREATE TABLE IF NOT EXISTS members (
            studentId TEXT PRIMARY KEY,
            titlePrefix TEXT,
            name TEXT,
            grade TEXT,
            major TEXT,
            club TEXT
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS clubs (
            name TEXT PRIMARY KEY,
            isActive BOOLEAN DEFAULT 1
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS clubQuotas (
            clubName TEXT PRIMARY KEY,
            maxMembers INTEGER
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activityName TEXT,
            date TEXT,
            club TEXT
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS attendance (
            activityId INTEGER,
            studentId TEXT,
            status TEXT,
            PRIMARY KEY (activityId, studentId)
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS systemStatus (
            key TEXT PRIMARY KEY,
            value BOOLEAN
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS admins (
            username TEXT PRIMARY KEY,
            password TEXT,
            name TEXT
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )`);

        db.get('SELECT COUNT(*) as count FROM admins', (err, row) => {
            if (row.count === 0) {
                db.run(`INSERT INTO admins (username, password, name) VALUES ('admin', 'admin', 'Administrator')`);
            }
        });
        
        db.get('SELECT COUNT(*) as count FROM systemStatus', (err, row) => {
            if (row.count === 0) {
                db.run(`INSERT INTO systemStatus (key, value) VALUES ('registrationOpen', 1)`);
            }
        });

        db.get('SELECT COUNT(*) as count FROM settings', (err, row) => {
            if (row.count === 0) {
                const defaultGradeList = ["ปวช. 1", "ปวช. 2", "ปวช. 3", "ปวส. 1", "ปวส. 2"];
                const defaultMajorList = {
                    'ปวช': ["เทคนิคคอมพิวเตอร์"],
                    'ปวส': ["เทคโนโลยีคอมพิวเตอร์", "โปรแกรมเมอร์", "เกมและอนิเมชั่น", "เครือข่ายคอมพิวเตอร์และความปลอดภัย"]
                };
                db.run(`INSERT INTO settings (key, value) VALUES (?, ?)`, ['gradeList', JSON.stringify(defaultGradeList)]);
                db.run(`INSERT INTO settings (key, value) VALUES (?, ?)`, ['majorList', JSON.stringify(defaultMajorList)]);
            }
        });
    });
}

app.get('/api/members', authenticateToken, (req, res) => {
    db.all('SELECT * FROM members', [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        const result = {};
        rows.forEach(r => result[r.studentId] = r);
        res.json(result);
    });
});

app.post('/api/members', (req, res) => {
    const { studentId, titlePrefix, name, grade, major, club } = req.body;
    db.run(
        `INSERT OR REPLACE INTO members (studentId, titlePrefix, name, grade, major, club) VALUES (?, ?, ?, ?, ?, ?)`,
        [studentId, titlePrefix, name, grade, major, club],
        function(err) {
            if (err) return res.status(500).json({ error: err.message });
            res.json({ message: 'Success', id: studentId });
        }
    );
});

app.delete('/api/members/:id', authenticateToken, (req, res) => {
    db.run(`DELETE FROM members WHERE studentId = ?`, req.params.id, function(err) {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ message: 'Deleted', changes: this.changes });
    });
});

app.get('/api/clubCounts', (req, res) => {
    db.all('SELECT club, COUNT(*) as count FROM members GROUP BY club', [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        const result = {};
        rows.forEach(r => result[r.club] = r.count);
        res.json(result);
    });
});

app.get('/api/publicMembers', (req, res) => {
    db.all('SELECT titlePrefix, name, grade, major, club FROM members', [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        
        const result = {};
        rows.forEach(r => {
            if (!result[r.club]) result[r.club] = [];
            result[r.club].push({ titlePrefix: r.titlePrefix, name: r.name, grade: r.grade, major: r.major });
        });
        res.json(result);
    });
});

app.get('/api/clubs', (req, res) => {
    db.all('SELECT * FROM clubs', [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        const result = {};
        rows.forEach(r => result[r.name] = r.isActive === 1 || r.isActive === true || r.isActive === 'true');
        res.json(result);
    });
});

app.post('/api/clubs', authenticateToken, (req, res) => {
    const { name, isActive } = req.body;
    db.run(
        `INSERT OR REPLACE INTO clubs (name, isActive) VALUES (?, ?)`,
        [name, isActive === true ? 1 : 0],
        function(err) {
            if (err) return res.status(500).json({ error: err.message });
            res.json({ message: 'Success' });
        }
    );
});

app.delete('/api/clubs/:name', authenticateToken, (req, res) => {
    db.serialize(() => {
        db.run(`DELETE FROM clubs WHERE name = ?`, req.params.name);
        db.run(`DELETE FROM clubQuotas WHERE clubName = ?`, req.params.name, function(err) {
            if (err) return res.status(500).json({ error: err.message });
            res.json({ message: 'Deleted' });
        });
    });
});

app.get('/api/clubQuotas', (req, res) => {
    db.all('SELECT * FROM clubQuotas', [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        const result = {};
        rows.forEach(r => result[r.clubName] = r.maxMembers);
        res.json(result);
    });
});

app.post('/api/clubQuotas', authenticateToken, (req, res) => {
    const { clubName, maxMembers } = req.body;
    db.run(
        `INSERT OR REPLACE INTO clubQuotas (clubName, maxMembers) VALUES (?, ?)`,
        [clubName, maxMembers],
        function(err) {
            if (err) return res.status(500).json({ error: err.message });
            res.json({ message: 'Success' });
        }
    );
});

app.get('/api/activities', (req, res) => {
    db.all('SELECT * FROM activities', [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        const result = {};
        rows.forEach(r => result[r.id] = r);
        res.json(result);
    });
});

app.post('/api/activities', authenticateToken, (req, res) => {
    const { activityName, date, club } = req.body;
    db.run(
        `INSERT INTO activities (activityName, date, club) VALUES (?, ?, ?)`,
        [activityName, date, club],
        function(err) {
            if (err) return res.status(500).json({ error: err.message });
            res.json({ id: this.lastID, activityName, date, club });
        }
    );
});

app.delete('/api/activities/:id', authenticateToken, (req, res) => {
    const id = req.params.id;
    db.serialize(() => {
        db.run(`DELETE FROM activities WHERE id = ?`, id);
        db.run(`DELETE FROM attendance WHERE activityId = ?`, id, function(err) {
            if (err) return res.status(500).json({ error: err.message });
            res.json({ message: 'Deleted' });
        });
    });
});

app.get('/api/attendance', (req, res) => {
    db.all('SELECT * FROM attendance', [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        const result = {};
        rows.forEach(r => {
            if (!result[r.activityId]) result[r.activityId] = {};
            result[r.activityId][r.studentId] = r.status;
        });
        res.json(result);
    });
});

app.get('/api/attendance/:activityId', (req, res) => {
    db.all('SELECT * FROM attendance WHERE activityId = ?', req.params.activityId, (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        const result = {};
        rows.forEach(r => result[r.studentId] = r.status);
        res.json(result);
    });
});

app.get('/api/publicAttendance/:activityId', (req, res) => {
    db.all(`
        SELECT m.titlePrefix, m.name, m.grade, m.major, m.club, COALESCE(a.status, 'ไม่มา') as status 
        FROM members m 
        LEFT JOIN attendance a ON m.studentId = a.studentId AND a.activityId = ?
    `, req.params.activityId, (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        const result = {};
        rows.forEach(r => {
            if (!result[r.club]) result[r.club] = [];
            result[r.club].push({
                titlePrefix: r.titlePrefix,
                name: r.name,
                grade: r.grade,
                major: r.major,
                status: r.status
            });
        });
        res.json(result);
    });
});

app.post('/api/attendance/:activityId/:studentId', authenticateToken, (req, res) => {
    const { activityId, studentId } = req.params;
    const { status } = req.body;
    db.run(
        `INSERT OR REPLACE INTO attendance (activityId, studentId, status) VALUES (?, ?, ?)`,
        [activityId, studentId, status],
        function(err) {
            if (err) return res.status(500).json({ error: err.message });
            res.json({ message: 'Success' });
        }
    );
});

app.get('/api/systemStatus', (req, res) => {
    db.get('SELECT * FROM systemStatus WHERE key = ?', ['registrationOpen'], (err, row) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ registrationOpen: row ? (row.value === 1 || row.value === 'true' || row.value === true) : true });
    });
});

app.post('/api/systemStatus', authenticateToken, (req, res) => {
    const { registrationOpen } = req.body;
    db.run(
        `INSERT OR REPLACE INTO systemStatus (key, value) VALUES (?, ?)`,
        ['registrationOpen', registrationOpen ? 1 : 0],
        function(err) {
            if (err) return res.status(500).json({ error: err.message });
            res.json({ message: 'Success' });
        }
    );
});

app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
    db.get('SELECT * FROM admins WHERE username = ? AND password = ?', [username, password], (err, row) => {
        if (err) return res.status(500).json({ error: err.message });
        if (row) {
            const token = jwt.sign({ username: row.username, name: row.name }, JWT_SECRET, { expiresIn: '1h' });
            res.json({ success: true, name: row.name, token });
        } else {
            res.status(401).json({ success: false, message: 'Invalid credentials' });
        }
    });
});

app.get('/api/admins', authenticateToken, (req, res) => {
    db.all('SELECT username, name, password FROM admins', [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        const result = {};
        rows.forEach(r => result[r.username] = { name: r.name, password: r.password });
        res.json(result);
    });
});

app.post('/api/admins', authenticateToken, (req, res) => {
    const { username, password, name } = req.body;
    db.run(
        `INSERT OR REPLACE INTO admins (username, password, name) VALUES (?, ?, ?)`,
        [username, password, name],
        function(err) {
            if (err) return res.status(500).json({ error: err.message });
            res.json({ message: 'Success' });
        }
    );
});

app.delete('/api/admins/:username', authenticateToken, (req, res) => {
    db.run(`DELETE FROM admins WHERE username = ?`, req.params.username, function(err) {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ message: 'Deleted' });
    });
});

app.get('/api/settings', (req, res) => {
    db.all('SELECT * FROM settings', [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        const result = {};
        rows.forEach(r => result[r.key] = JSON.parse(r.value));
        res.json(result);
    });
});

app.post('/api/settings', authenticateToken, (req, res) => {
    const { key, value } = req.body;
    db.run(`INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value`, 
        [key, JSON.stringify(value)], 
        function(err) {
            if (err) return res.status(500).json({ error: err.message });
            res.json({ success: true });
        }
    );
});

app.get('/api/systemStats', authenticateToken, (req, res) => {
    let stats = {};
    
    try {
        const statsObj = fs.statSync(DB_PATH);
        stats.dbSizeBytes = statsObj.size;
        stats.dbPath = path.resolve(DB_PATH);
    } catch (e) {
        stats.dbSizeBytes = 0;
    }

    db.get('SELECT COUNT(*) as count FROM members', [], (err, row) => {
        stats.memberCount = row ? row.count : 0;
        db.get('SELECT COUNT(*) as count FROM clubs', [], (err, row) => {
            stats.clubCount = row ? row.count : 0;
            res.json(stats);
        });
    });
});

app.get('/api/backup', (req, res) => {
    const token = req.query.token;
    if (!token) return res.status(401).send('Unauthorized');
    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) return res.status(403).send('Forbidden');
        res.download(path.resolve(DB_PATH), 'database_backup.sqlite');
    });
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
