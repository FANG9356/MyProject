let allMembers = [];
let allActivities = [];
let currentClub = '';
let currentActivityId = null;
let dynamicClubList = [];

const clubSelect = document.getElementById('club-select');
const activitySelect = document.getElementById('activity-select');
const memberListDiv = document.getElementById('member-list');
const activityModal = document.getElementById('activity-modal');
const activityForm = document.getElementById('activity-form');
const deleteActivityBtn = document.getElementById('delete-activity-btn');

async function fetchAllData() {
    try {
        const clubsRes = await fetch('/api/clubs');
        const clubsData = await clubsRes.json();

        dynamicClubList = Object.keys(clubsData).sort((a, b) => {
            const activeA = clubsData[a] ? 1 : 0;
            const activeB = clubsData[b] ? 1 : 0;
            if (activeA !== activeB) return activeB - activeA;
            return a.localeCompare(b);
        });

        const currentSelected = clubSelect.value;
        clubSelect.innerHTML = `<option value="">-- เลือกชมรม --</option>` +
            dynamicClubList.map(club => {
                if (clubsData[club]) {
                    return `<option value="${club}" class="text-gray-800">${club}</option>`;
                } else {
                    return `<option value="${club}" class="text-rose-500 bg-rose-50">${club} (ปิดชั่วคราว)</option>`;
                }
            }).join('');

        if (dynamicClubList.includes(currentSelected)) {
            clubSelect.value = currentSelected;
        }

        const memRes = await fetch('/api/members');
        const memData = await memRes.json();
        allMembers = Object.values(memData);

        const actRes = await fetch('/api/activities');
        const actData = await actRes.json();
        allActivities = Object.values(actData);

        renderActivities();
        if (currentClub) {
            renderAttendanceList();
        }
    } catch (e) {
        console.error(e);
    }
}

function renderActivities() {
    const filteredActivities = allActivities.filter(act => act.club === currentClub);

    activitySelect.innerHTML = `<option value="">-- เลือกกิจกรรม --</option>` + filteredActivities.map(act => {
        const formattedDate = act.date ? new Date(act.date).toLocaleDateString('th-TH') : '';
        return `<option value="${act.id}">${act.activityName} (${formattedDate})</option>`;
    }).join('');

    if (!filteredActivities.find(act => String(act.id) === String(currentActivityId))) {
        currentActivityId = null;
    }
    activitySelect.value = currentActivityId || '';

    if (currentActivityId) {
        deleteActivityBtn.classList.remove('hidden');
    } else {
        deleteActivityBtn.classList.add('hidden');
    }
}

async function renderAttendanceList() {
    if (!currentActivityId || !currentClub) {
        memberListDiv.innerHTML = '<p class="text-gray-500 text-center py-8">กรุณาเลือกทั้งชมรมและกิจกรรมเพื่อเช็กชื่อ</p>';
        return;
    }
    const clubMembers = allMembers.filter(member => member.club === currentClub);

    try {
        const res = await fetch(`/api/attendance/${currentActivityId}`);
        const attendanceData = await res.json();

        const memberHTML = clubMembers.sort((a, b) => a.studentId.localeCompare(b.studentId)).map(member => {
            const status = attendanceData[member.studentId] || 'ไม่มา';
            return `
                <div class="flex items-center justify-between p-3 border-b border-gray-200 last:border-b-0">
                    <div class="flex-grow">
                        <p class="text-sm font-semibold">${member.titlePrefix} ${member.name}</p>
                        <p class="text-xs text-gray-500">${member.studentId} | ${member.grade}</p>
                    </div>
                    <div>
                        <select onchange="updateAttendance('${member.studentId}', this.value)" class="p-2 border rounded-md outline-none focus:ring-2 focus:ring-indigo-500">
                            <option value="มา" ${status === 'มา' ? 'selected' : ''}>มา</option>
                            <option value="ไม่มา" ${status === 'ไม่มา' ? 'selected' : ''}>ไม่มา</option>
                            <option value="ลา" ${status === 'ลา' ? 'selected' : ''}>ลา</option>
                        </select>
                    </div>
                </div>
            `;
        }).join('');
        memberListDiv.innerHTML = memberHTML || '<p class="text-gray-500 text-center py-8">ยังไม่มีสมาชิกในชมรมนี้</p>';
    } catch(e) {
        console.error(e);
    }
}

window.updateAttendance = async function(studentId, status) {
    if (currentActivityId) {
        try {
            await fetch(`/api/attendance/${currentActivityId}/${studentId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status })
            });
        } catch(e) {
            console.error('Failed to update status', e);
        }
    }
}

window.deleteActivity = async function() {
    if (!currentActivityId) {
        alert('กรุณาเลือกกิจกรรมที่ต้องการลบ');
        return;
    }
    if (confirm("คุณแน่ใจหรือไม่ว่าต้องการลบกิจกรรมนี้?")) {
        try {
            await fetch(`/api/activities/${currentActivityId}`, {
                method: 'DELETE'
            });
            currentActivityId = null;
            activitySelect.value = '';
            deleteActivityBtn.classList.add('hidden');
            alert('ลบกิจกรรมเรียบร้อยแล้ว');
            fetchAllData();
        } catch(e) {
            alert('Error deleting activity');
        }
    }
}

clubSelect.addEventListener('change', () => {
    currentClub = clubSelect.value;
    currentActivityId = null;
    renderActivities();
    renderAttendanceList();
});

activitySelect.addEventListener('change', () => {
    currentActivityId = activitySelect.value;
    renderAttendanceList();
    if (currentActivityId) {
        deleteActivityBtn.classList.remove('hidden');
    } else {
        deleteActivityBtn.classList.add('hidden');
    }
});

window.openActivityModal = function() {
    if (!currentClub) {
        alert('กรุณาเลือกชมรมก่อนสร้างกิจกรรมครับ!');
        return;
    }
    activityModal.classList.remove('hidden');
}

activityForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const activityName = document.getElementById('activity-name').value;
    const activityDate = document.getElementById('activity-date').value;

    if (activityName && activityDate && currentClub) {
        try {
            await fetch('/api/activities', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    activityName: activityName,
                    date: activityDate,
                    club: currentClub
                })
            });
            alert('สร้างกิจกรรมสำหรับชมรมเรียบร้อยแล้ว');
            activityModal.classList.add('hidden');
            activityForm.reset();
            fetchAllData();
        } catch (error) {
            alert('เกิดข้อผิดพลาดในการสร้างกิจกรรม: ' + error.message);
        }
    } else {
        alert('กรุณากรอกข้อมูลให้ครบถ้วน');
    }
});

const adminName = sessionStorage.getItem('adminName');
checkSession('admin.html');
if (adminName) document.getElementById('admin-name-display').innerText = 'ผู้ใช้งาน: ' + adminName;
startSessionTimer('admin.html');

const _origFetch = window.fetch;
window.fetch = async function(resource, config) {
    const tok = sessionStorage.getItem('token');
    if (tok && typeof resource === 'string' && resource.startsWith('/api/')) {
        config = config || {};
        config.headers = { ...(config.headers || {}), 'Authorization': 'Bearer ' + tok };
    }
    const res = await _origFetch(resource, config);
    if ((res.status === 401 || res.status === 403) && resource.startsWith('/api/')) {
        clearSession('admin.html');
    }
    return res;
};

function logout() { clearSession('admin.html'); }

fetchAllData();
setInterval(fetchAllData, 10000);
