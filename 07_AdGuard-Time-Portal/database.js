const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.resolve(__dirname, 'database.sqlite');
const db = new sqlite3.Database(dbPath);

db.serialize(() => {
    db.run(`
        CREATE TABLE IF NOT EXISTS pins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pin TEXT UNIQUE NOT NULL,
            duration_hours INTEGER NOT NULL,
            is_used BOOLEAN DEFAULT 0,
            used_at INTEGER,
            expires_at INTEGER
        )
    `);
});

module.exports = db;
