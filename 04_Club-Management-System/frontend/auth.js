const SESSION_DURATION = 30 * 60 * 1000;

function checkSession(loginPath = 'admin.html') {
    const adminName = sessionStorage.getItem('adminName');
    const loginTimestamp = sessionStorage.getItem('loginTimestamp');
    const token = sessionStorage.getItem('token');

    if (!adminName || !loginTimestamp || !token) {
        window.location.href = loginPath;
        return null;
    }

    const timeElapsed = Date.now() - parseInt(loginTimestamp);
    if (timeElapsed > SESSION_DURATION) {
        clearSession(loginPath);
        return null;
    }

    return token;
}

function clearSession(loginPath = 'admin.html') {
    sessionStorage.removeItem('adminName');
    sessionStorage.removeItem('loginTimestamp');
    sessionStorage.removeItem('token');
    alert('เซสชันของคุณหมดอายุแล้ว (ครบ 30 นาที) กรุณาเข้าสู่ระบบใหม่');
    window.location.href = loginPath;
}

function authHeaders() {
    const token = sessionStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

async function authFetch(url, options = {}, loginPath = 'admin.html') {
    const token = sessionStorage.getItem('token');
    const mergedOptions = {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {}),
            'Authorization': `Bearer ${token}`
        }
    };

    const res = await fetch(url, mergedOptions);

    if (res.status === 401 || res.status === 403) {
        clearSession(loginPath);
        return null;
    }

    return res;
}

function startSessionTimer(loginPath = 'admin.html') {
    const loginTimestamp = sessionStorage.getItem('loginTimestamp');
    if (!loginTimestamp) return;

    const timeElapsed = Date.now() - parseInt(loginTimestamp);
    const timeRemaining = SESSION_DURATION - timeElapsed;

    if (timeRemaining <= 0) {
        clearSession(loginPath);
        return;
    }

    setTimeout(() => clearSession(loginPath), timeRemaining);
}

function blockDevTools() {
    document.addEventListener('contextmenu', e => e.preventDefault());
    document.addEventListener('keydown', e => {
        if (e.key === 'F12') { e.preventDefault(); return false; }
        if (e.ctrlKey && e.shiftKey && ['I', 'J', 'C', 'i', 'j', 'c'].includes(e.key)) { e.preventDefault(); return false; }
        if (e.ctrlKey && ['u', 'U'].includes(e.key)) { e.preventDefault(); return false; }
        if (e.ctrlKey && e.shiftKey && e.key === 'K') { e.preventDefault(); return false; }
    });

    let devtoolsOpen = false;
    const threshold = 160;
    setInterval(() => {
        const widthDiff = window.outerWidth - window.innerWidth;
        const heightDiff = window.outerHeight - window.innerHeight;
        if (widthDiff > threshold || heightDiff > threshold) {
            if (!devtoolsOpen) {
                devtoolsOpen = true;
                document.body.innerHTML = `
                    <div style="display:flex;align-items:center;justify-content:center;height:100vh;flex-direction:column;background:#f8fafc;font-family:sans-serif;">
                        <div style="font-size:64px;">🔒</div>
                        <h1 style="color:#ef4444;font-size:28px;margin:16px 0 8px">การเข้าถึงถูกปิดกั้น</h1>
                        <p style="color:#64748b;font-size:16px">ปิด Developer Tools แล้วรีเฟรชหน้าเว็บ</p>
                    </div>`;
            }
        } else {
            devtoolsOpen = false;
        }
    }, 1000);
}
