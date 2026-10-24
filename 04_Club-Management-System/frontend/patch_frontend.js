const fs = require('fs');
const path = require('path');

const antiF12Script = `
    <!-- Anti F12 & Right Click -->
    <script>
        document.addEventListener('contextmenu', event => event.preventDefault());
        document.onkeydown = function(e) {
            if(e.keyCode == 123) return false; // F12
            if(e.ctrlKey && e.shiftKey && (e.keyCode == 'I'.charCodeAt(0) || e.keyCode == 'J'.charCodeAt(0) || e.keyCode == 'C'.charCodeAt(0))) return false; // Ctrl+Shift+I/J/C
            if(e.ctrlKey && e.keyCode == 'U'.charCodeAt(0)) return false; // Ctrl+U
        }
    </script>
`;

const fetchInterceptor = `
        // Global Fetch Interceptor for JWT
        const originalFetch = window.fetch;
        window.fetch = async function() {
            let [resource, config] = arguments;
            const token = sessionStorage.getItem('token');
            if (token && typeof resource === 'string' && resource.startsWith('/api/')) {
                config = config || {};
                config.headers = config.headers || {};
                config.headers['Authorization'] = 'Bearer ' + token;
            }
            const res = await originalFetch(resource, config);
            if (res.status === 401 || res.status === 403) {
                if (typeof logout === 'function') logout();
            }
            return res;
        };
`;

function patchFile(file) {
    let content = fs.readFileSync(file, 'utf8');
    
    // Add antiF12 before </head> if not exists
    if (!content.includes('Anti F12 & Right Click') && !file.endsWith('.js')) {
        content = content.replace('</head>', antiF12Script + '\n</head>');
    }
    
    // If it's admin.html, save the token
    if (file.endsWith('admin.html')) {
        content = content.replace("sessionStorage.setItem('loginTimestamp', Date.now());", "sessionStorage.setItem('loginTimestamp', Date.now());\n                    sessionStorage.setItem('token', data.token);");
        content = content.replace("sessionStorage.removeItem('loginTimestamp');", "sessionStorage.removeItem('loginTimestamp');\n                sessionStorage.removeItem('token');");
    }
    
    // Admin pages logic
    if (file.endsWith('data.html') || file.endsWith('attendance.js') || file.endsWith('superadmin/index (1).html')) {
        if (!content.includes('Global Fetch Interceptor')) {
            content = content.replace('function enforceSession() {', fetchInterceptor + '\n        function enforceSession() {');
        }
        content = content.replace("sessionStorage.removeItem('loginTimestamp');", "sessionStorage.removeItem('loginTimestamp');\n            sessionStorage.removeItem('token');");
        // Update backup link in superadmin
        if (file.endsWith('superadmin/index (1).html')) {
            content = content.replace('href="/api/backup"', 'href="#" onclick="window.open(\'/api/backup?token=\' + sessionStorage.getItem(\'token\'), \'_blank\')"');
        }
    }

    // register.html logic: Use clubCounts instead of members
    if (file.endsWith('register.html')) {
        content = content.replace("const memRes = await fetch('/api/members');", "const memRes = await fetch('/api/clubCounts');");
        content = content.replace("const memData = await memRes.json();\n                membersData = Object.values(memData);", "const memData = await memRes.json();\n                membersData = memData; // Dictionary of club: count");
        content = content.replace("const count = membersData.filter(m => m.club === selectedClub).length;", "const count = membersData[selectedClub] || 0;");
    }
    
    fs.writeFileSync(file, content, 'utf8');
    console.log('Patched ' + file);
}

const frontendDir = '/Volumes/FangB/club/frontend';
const files = [
    'index.html',
    'register.html',
    'data.html',
    'admin.html',
    'attendance.html',
    'attendance.js',
    'superadmin/index (1).html'
];

files.forEach(f => {
    try {
        patchFile(path.join(frontendDir, f));
    } catch(e) {
        console.error("Error patching " + f, e);
    }
});
