const fs = require('fs');

let content = fs.readFileSync('server.js', 'utf8');

const jwtImport = `const fs = require('fs');
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
`;
content = content.replace("const fs = require('fs');", jwtImport);

const clubCountsEndpoint = `
app.get('/api/clubCounts', (req, res) => {
    db.all('SELECT club, COUNT(*) as count FROM members GROUP BY club', [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        const result = {};
        rows.forEach(r => result[r.club] = r.count);
        res.json(result);
    });
});
`;
content = content.replace("app.get('/api/clubs'", clubCountsEndpoint + "\napp.get('/api/clubs'");

const loginEndpointOld = `app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
    db.get('SELECT * FROM admins WHERE username = ? AND password = ?', [username, password], (err, row) => {
        if (err) return res.status(500).json({ error: err.message });
        if (row) {
            res.json({ success: true, name: row.name });
        } else {
            res.status(401).json({ success: false, message: 'Invalid credentials' });
        }
    });
});`;
const loginEndpointNew = `app.post('/api/login', (req, res) => {
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
});`;
content = content.replace(loginEndpointOld, loginEndpointNew);

const protectedRoutes = [
    "app.get('/api/members',",
    "app.post('/api/members',",
    "app.delete('/api/members/:id',",
    "app.post('/api/clubs',",
    "app.delete('/api/clubs/:name',",
    "app.post('/api/clubQuotas',",
    "app.post('/api/activities',",
    "app.delete('/api/activities/:id',",
    "app.post('/api/attendance/:activityId/:studentId',",
    "app.post('/api/systemStatus',",
    "app.get('/api/admins',",
    "app.post('/api/admins',",
    "app.delete('/api/admins/:username',",
    "app.post('/api/settings',",
    "app.get('/api/systemStats',"
];
protectedRoutes.forEach(route => {
    content = content.replace(route, route.replace(',', ', authenticateToken,'));
});

const backupEndpointOld = `app.get('/api/backup', (req, res) => {
    res.download(path.resolve(DB_PATH), 'database_backup.sqlite');
});`;
const backupEndpointNew = `app.get('/api/backup', (req, res) => {
    const token = req.query.token;
    if (!token) return res.status(401).send('Unauthorized');
    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) return res.status(403).send('Forbidden');
        res.download(path.resolve(DB_PATH), 'database_backup.sqlite');
    });
});`;
content = content.replace(backupEndpointOld, backupEndpointNew);

fs.writeFileSync('server.js', content, 'utf8');
console.log('Patched server.js');
