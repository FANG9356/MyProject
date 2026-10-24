let bookingQueue = [];
let currentIndex = -1;
let dragStartIndex = -1;
const player = document.getElementById('player');
const videoCard = document.querySelector('.video-card');
const dynamicBg = document.getElementById('dynamic-bg');
let suggestTimeout;

document.addEventListener('contextmenu', event => event.preventDefault());

// 🔥 [ไฮไลต์] เมื่อวิดีโอโหลดเสร็จ ให้อ่านสัดส่วนแล้วสั่งให้กรอบค่อยๆ ขยับตาม!
player.addEventListener('loadedmetadata', () => {
    if (player.videoWidth && player.videoHeight) {
        const ratio = player.videoWidth / player.videoHeight;
        player.style.aspectRatio = `${ratio}`; // ดึงขนาดจริงส่งให้ CSS แปลงร่างแบบสมูท
    }
});

const canvas = document.createElement('canvas');
canvas.width = 5; canvas.height = 5;
const ctx = canvas.getContext('2d', { willReadFrequently: true });

function getDynamicColor() {
    if (player.paused || player.ended || !player.src) return null;
    try {
        ctx.drawImage(player, 0, 0, canvas.width, canvas.height);
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;
        let r = 0, g = 0, b = 0, count = 0;
        for (let i = 0; i < data.length; i += 4) { r += data[i]; g += data[i + 1]; b += data[i + 2]; count++; }
        r = Math.floor(r / count); g = Math.floor(g / count); b = Math.floor(b / count);
        return `${r}, ${g}, ${b}`;
    } catch (e) { return null; }
}

// 🎯 อัปเดตออร่าและสี Address Bar แบบเรียลไทม์
// function updateGlow() {
//     const rgbStr = getDynamicColor();
//     if (rgbStr) {
//         document.documentElement.style.setProperty('--theme-rgb', rgbStr);
//         videoCard.style.setProperty('--glow-color', `rgba(${rgbStr}, 0.35)`);
//         dynamicBg.style.background = `rgba(${rgbStr}, 0.45)`;

//         // 🔥 [ฟีเจอร์ใหม่] เปลี่ยนสี Address Bar (Top Bar) ด้านบนเบราว์เซอร์
//         let metaTheme = document.querySelector("meta[name='theme-color']");
//         if (!metaTheme) {
//             metaTheme = document.createElement("meta");
//             metaTheme.name = "theme-color";
//             document.head.appendChild(metaTheme);
//         }
//         // ย้อมสี Address Bar ให้เข้ากับโทนวิดีโอแบบเนียนๆ
//         metaTheme.setAttribute("content", `rgb(${rgbStr})`); 
//     }
// }
/* =========================================
   🎨 [Dynamic Theme] ระบบโช้คอัพสี + กรอง Noise
   ========================================= */
// let currentRGB = [0, 113, 227]; // สีที่กำลังโชว์อยู่ตอนนี้
// let targetRGB = [0, 113, 227];  // สีเป้าหมายที่ดูดได้จากวิดีโอ

// function updateGlow() {
//     const rgbStr = getDynamicColor();
//     if (!rgbStr) return;

//     const newColors = rgbStr.split(',').map(Number);

//     // 1. 🛡️ ระบบกรอง Noise: เทียบสีที่เพิ่งดูดมา กับ สีเป้าหมายล่าสุด
//     const diff = Math.abs(newColors[0] - targetRGB[0]) + 
//                  Math.abs(newColors[1] - targetRGB[1]) + 
//                  Math.abs(newColors[2] - targetRGB[2]);

//     // ถ้าสีเปลี่ยนเกิน 10 หน่วย (ไม่ใช่แค่ Noise ของภาพนิ่ง) ค่อยอัปเดตเป้าหมายใหม่
//     if (diff > 10) {
//         targetRGB = newColors;
//     }

//     // 2. 🌊 ระบบโช้คอัพ (Lerp): บังคับให้สีปัจจุบัน ค่อยๆ ขยับไปหาสีเป้าหมายทีละ 10%
//     // (ทำให้สีเปลี่ยนนุ่มนวลมาก ไหลลื่นเหมือนน้ำ ไม่มีการกระโดดข้ามค่า)
//     currentRGB[0] += (targetRGB[0] - currentRGB[0]) * 0.1;
//     currentRGB[1] += (targetRGB[1] - currentRGB[1]) * 0.1;
//     currentRGB[2] += (targetRGB[2] - currentRGB[2]) * 0.1;

//     // ปัดเศษให้เป็นตัวเลขที่ CSS เอาไปใช้ได้
//     const r = Math.round(currentRGB[0]);
//     const g = Math.round(currentRGB[1]);
//     const b = Math.round(currentRGB[2]);
//     const smoothRgbStr = `${r}, ${g}, ${b}`;

//     // 3. ส่งสีที่นุ่มละมุนแล้วไปให้หน้าเว็บ
//     document.documentElement.style.setProperty('--theme-rgb', smoothRgbStr);

//     // อัปเดตเงาวิดีโอและฉากหลัง
//     const videoCard = document.querySelector('.video-card');
//     const dynamicBg = document.getElementById('dynamic-bg');
//     if (videoCard) videoCard.style.setProperty('--glow-color', `rgba(${smoothRgbStr}, 0.35)`);
//     if (dynamicBg) dynamicBg.style.background = `rgba(${smoothRgbStr}, 0.45)`;

//     // ย้อมสี Address Bar (Top Bar) ด้านบนเบราว์เซอร์
//     let metaTheme = document.querySelector("meta[name='theme-color']");
//     if (!metaTheme) {
//         metaTheme = document.createElement("meta");
//         metaTheme.name = "theme-color";
//         document.head.appendChild(metaTheme);
//     }
//     metaTheme.setAttribute("content", `rgb(${smoothRgbStr})`); 
// } 

// // เอาไปวางในหน้าเว็บฝั่งเครื่องเล่น (บน Mac)
// player.addEventListener('volumechange', () => {
//     const currentVol = player.volume;

//     // อัปเดตหลอดบนหน้าจอ Mac ให้ตรงกัน
//     if (document.getElementById('volumeSlider')) {
//         document.getElementById('volumeSlider').value = currentVol;
//     }

//     // ส่งค่ากลับไปบอก Server หลังบ้าน
//     fetch('/remote/updateState', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ volume: currentVol })
//     }).catch(err => console.log("ส่งสถานะกลับไม่สำเร็จ:", err));
// });

/* =========================================
   🎨 [Dynamic Theme] ระบบโช้คอัพสี + เบรคเกอร์ตัดไฟ!
   ========================================= */
let currentRGB = [0, 113, 227];
let targetRGB = [0, 113, 227];
let lastRenderedRGB = ""; // 🛑 ตัวแปรใหม่ เอาไว้จำสีล่าสุด!

function updateGlow() {
    const rgbStr = getDynamicColor();
    if (!rgbStr) return;

    const newColors = rgbStr.split(',').map(Number);

    // 1. 🛡️ ขยายกำแพงกรอง Noise: ปรับความแข็งเป็น 25 หน่วย (วิดีโอภาพนิ่งจะได้ไม่ดิ้น)
    const diff = Math.abs(newColors[0] - targetRGB[0]) +
        Math.abs(newColors[1] - targetRGB[1]) +
        Math.abs(newColors[2] - targetRGB[2]);

    if (diff > 25) {
        targetRGB = newColors;
    }

    // 2. 🌊 ระบบโช้คอัพ (Lerp): ขยับทีละ 20% ให้เข้าเป้าไวขึ้น นุ่มนวลแต่ไม่ยืดเยื้อ
    currentRGB[0] += (targetRGB[0] - currentRGB[0]) * 0.2;
    currentRGB[1] += (targetRGB[1] - currentRGB[1]) * 0.2;
    currentRGB[2] += (targetRGB[2] - currentRGB[2]) * 0.2;

    const r = Math.round(currentRGB[0]);
    const g = Math.round(currentRGB[1]);
    const b = Math.round(currentRGB[2]);
    const smoothRgbStr = `${r}, ${g}, ${b}`;

    // 🛑 3. ไม้ตาย "เบรคเกอร์ตัดไฟ": ถ้าสีใหม่ตรงกับสีเก่าเป๊ะๆ ให้หยุดทำงานทันที!
    // (จุดนี้แหละที่จะช่วยชีวิตเบราว์เซอร์ไม่ให้ต้องเรนเดอร์กระจกฝ้ารัวๆ)
    if (smoothRgbStr === lastRenderedRGB) return;
    lastRenderedRGB = smoothRgbStr; // ถ้าสีเปลี่ยน ค่อยจดจำสีใหม่

    // 4. ส่งสีไปให้หน้าเว็บ
    document.documentElement.style.setProperty('--theme-rgb', smoothRgbStr);

    const videoCard = document.querySelector('.video-card');
    const dynamicBg = document.getElementById('dynamic-bg');
    if (videoCard) videoCard.style.setProperty('--glow-color', `rgba(${smoothRgbStr}, 0.35)`);
    if (dynamicBg) dynamicBg.style.background = `rgba(${smoothRgbStr}, 0.45)`;

    let metaTheme = document.querySelector("meta[name='theme-color']");
    if (!metaTheme) {
        metaTheme = document.createElement("meta");
        metaTheme.name = "theme-color";
        document.head.appendChild(metaTheme);
    }
    metaTheme.setAttribute("content", `rgb(${smoothRgbStr})`);
}

// setInterval(updateGlow, 100); 
setInterval(updateGlow, 100); // อัปเดตทุก 100ms จะได้ไม่หน่วงเกินไป แต่ยังดูไดนามิกอยู่

let idleTimer;
const idleLimit = 6000;

function resetIdleTimer() {
    document.body.classList.remove('idle-mode');
    clearTimeout(idleTimer);
    if (player && !player.paused && player.src) {
        idleTimer = setTimeout(() => {
            if (!document.body.classList.contains('theater-mode')) {
                document.body.classList.add('idle-mode');
            }
        }, idleLimit);
    }
}

['mousemove', 'keydown', 'mousedown', 'touchstart', 'scroll'].forEach(evt => {
    document.addEventListener(evt, resetIdleTimer);
});

// setInterval(() => {
//     const rgbStr = getDynamicColor() || '0, 113, 227';
//     const currentTitle = document.getElementById('currentSongTitle').innerText;
//     let nextTitle = document.getElementById('upNextDisplay').innerText.replace('ถัดไป:', '').trim();
//     if(nextTitle === '-' || nextTitle === '') nextTitle = '-';

//     fetch(`/state/update?rgb=${encodeURIComponent(rgbStr)}&current=${encodeURIComponent(currentTitle)}&next_song=${encodeURIComponent(nextTitle)}&playing=${!player.paused}`)
//     .catch(e=>{});
// }, 1000);
// 📡 ส่งข้อมูลอัปเดตไปให้ Server (มือถือจะได้เห็น)
// setInterval(() => {
//     const rgbStr = getDynamicColor() || '0, 113, 227';
//     const currentTitle = document.getElementById('currentSongTitle').innerText;
//     let nextTitle = document.getElementById('upNextDisplay').innerText.replace('ถัดไป:', '').trim();
//     if(nextTitle === '-' || nextTitle === '') nextTitle = '-';

//     // 🖼️ ดึงรูปหน้าปกจาก YouTube
//     let thumbUrl = "";
//     if (currentIndex !== -1 && bookingQueue[currentIndex]) {
//         const url = bookingQueue[currentIndex].url || "";
//         const match = url.match(/v=([^&]+)/);
//         if (match) thumbUrl = `https://i.ytimg.com/vi/${match[1]}/hqdefault.jpg`;
//     }

//     // ⏱️ ดึงเวลาเพลง
//     const time = player.currentTime || 0;
//     const duration = player.duration || 0;

//     // ส่งทั้งหมดไปเข้า API
//     fetch(`/state/update?rgb=${encodeURIComponent(rgbStr)}&current=${encodeURIComponent(currentTitle)}&next_song=${encodeURIComponent(nextTitle)}&playing=${!player.paused}&thumb=${encodeURIComponent(thumbUrl)}&time=${time}&duration=${duration}`)
//     .catch(e=>{});
// }, 1000);
// 📡 ส่งข้อมูลอัปเดตไปให้ Server (มือถือจะได้เห็น)
// 📡 ส่งข้อมูลอัปเดตไปให้ Server + ระบบ AI ดึงหน้าปกสุดโหด!
setInterval(() => {
    const rgbStr = getDynamicColor() || '0, 113, 227';
    const currentTitle = document.getElementById('currentSongTitle').innerText;
    let nextTitle = document.getElementById('upNextDisplay').innerText.replace('ถัดไป:', '').trim();
    if (nextTitle === '-' || nextTitle === '') nextTitle = '-';

    // 🖼️ ระบบหาปกอัจฉริยะ (ทำงานอิสระ ไม่โดนฟังก์ชันอื่นทับแน่นอน)
    let thumbUrl = "";
    const song = bookingQueue[currentIndex];

    if (song) {
        // เคสที่ 1: เป็นเพลงใหม่เพิ่งเพิ่ม มีลิงก์ YouTube แกะรูปลงได้เลยทันที!
        if (song.url && song.url.includes('v=')) {
            const match = song.url.match(/v=([^&]+)/);
            if (match) {
                thumbUrl = `https://i.ytimg.com/vi/${match[1]}/hqdefault.jpg`;
                song.thumb = thumbUrl; // จำไว้ใช้รอบหน้า
            }
        }
        // เคสที่ 2: เพลงเก่าโหลดจากเครื่อง ไม่มีลิงก์ ให้ AI แอบไปค้นมาให้
        else if (!song.thumb) {
            song.thumb = "searching"; // แปะป้ายไว้ก่อนว่ากำลังหา จะได้ไม่หาซ้ำรัวๆ
            const query = song.title || song;
            fetch(`/search?q=${encodeURIComponent(query)}`)
                .then(r => r.json())
                .then(data => {
                    if (data && data.length > 0 && data[0].thumbnail) {
                        song.thumb = data[0].thumbnail; // เจอรูปแล้ว!
                    } else {
                        song.thumb = "notfound";
                    }
                }).catch(() => { });
        }

        // ถ้าระบบหาเจอแล้ว ก็เอามาส่งให้มือถือได้เลย
        if (!thumbUrl && song.thumb && song.thumb !== "searching" && song.thumb !== "notfound") {
            thumbUrl = song.thumb;
        }
    }

    // ⏱️ ดึงเวลาเพลง
    const time = player.currentTime || 0;
    const duration = player.duration || 0;

    // ยิงขึ้น Server ให้หมด
    // แก้เฉพาะบรรทัดที่ 293 ใน script.js
    const currentVolSlider = document.getElementById('volumeSlider') ? document.getElementById('volumeSlider').value : 1;

    fetch(`/state/update?rgb=${encodeURIComponent(rgbStr)}&current=${encodeURIComponent(currentTitle)}&next_song=${encodeURIComponent(nextTitle)}&playing=${!player.paused}&thumb=${encodeURIComponent(thumbUrl)}&time=${time}&duration=${duration}&vol=${currentVolSlider}`) // 🔥 เปลี่ยนจาก player.volume เป็น currentVolSlider
        .catch(e => { });
}, 1000);


setInterval(async () => {
    try {
        const res = await fetch('/remote/poll');
        const data = await res.json();

        if (data.command) {
            if (data.command === 'playpause') {
                togglePlay();
            } else if (data.command === 'next') {
                playNext();
            } else if (data.command === 'prev') {
                playPrevious();
            }
            // 🔥 ใช้ smoothVolumeChange และอัปเดตหลอดสไลด์ในบล็อกเดียวกันเลย
            else if (data.command === 'volup') {
                const newVol = Math.min(1, player.volume + 0.1);
                smoothVolumeChange(newVol);
                if (document.getElementById('volumeSlider')) {
                    document.getElementById('volumeSlider').value = newVol;
                }
            }
            else if (data.command === 'voldown') {
                const newVol = Math.max(0, player.volume - 0.1);
                smoothVolumeChange(newVol);
                if (document.getElementById('volumeSlider')) {
                    document.getElementById('volumeSlider').value = newVol;
                }
            }
            else if (data.command.startsWith('setvol:')) {
                const v = parseFloat(data.command.split(':')[1]);
                smoothVolumeChange(v);
                if (document.getElementById('volumeSlider')) {
                    document.getElementById('volumeSlider').value = v;
                }
            }

            resetIdleTimer();
        }
    } catch (e) {
        // ปล่อยว่างไว้จัดการ error (ถ้ามี) 
    }
}, 1000);

// ระบบคีย์ลัดบนคีย์บอร์ด
document.addEventListener('keydown', (e) => {
    // ถ้ากำลังพิมพ์หาเพลงอยู่ จะไม่ให้คีย์ลัดทำงาน
    if (e.target.tagName === 'INPUT') return;

    if (e.code === 'Space') { e.preventDefault(); togglePlay(); }
    else if (e.code === 'ArrowRight') { e.preventDefault(); playNext(); }
    else if (e.code === 'ArrowLeft') { e.preventDefault(); playPrevious(); }

    // 🔥 เพิ่มคีย์ลัดลูกศรขึ้น/ลง สำหรับปรับเสียง (ทีละ 10%)
    else if (e.code === 'ArrowUp') {
        e.preventDefault();
        const slider = document.getElementById('volumeSlider');
        slider.value = Math.min(1, parseFloat(slider.value) + 0.1); // ห้ามดังเกิน 100%
        changeVolume();
    }
    else if (e.code === 'ArrowDown') {
        e.preventDefault();
        const slider = document.getElementById('volumeSlider');
        slider.value = Math.max(0, parseFloat(slider.value) - 0.1); // ห้ามเบากว่า 0%
        changeVolume();
    }

    else if (e.key.toLowerCase() === 't') { e.preventDefault(); toggleTheater(); }
    else if (e.key.toLowerCase() === 'p') { e.preventDefault(); togglePiP(); }
    else if (e.key.toLowerCase() === 'm') { e.preventDefault(); toggleMute(); }
    else if (e.key.toLowerCase() === 'f') { e.preventDefault(); toggleFullScreen(); }
    else if (e.key.toLowerCase() === 'a') { e.preventDefault(); toggleAutoPlay(); }
    else if (e.key.toLowerCase() === 'k') { e.preventDefault(); toggleLyrics(); }
});

function toggleTheater() {
    document.body.classList.toggle('theater-mode');
    resetIdleTimer();
}

function togglePlay() { player.paused ? player.play() : player.pause(); }
// function changeVolume() { player.volume = document.getElementById('volumeSlider').value; }

/* =========================================
   ✨ [Pro UX] ฟังก์ชันเสริมระดับพรีเมียม
   ========================================= */

// โหลดระดับเสียงที่จำไว้ตอนเปิดเว็บ
window.addEventListener('DOMContentLoaded', () => {
    const savedVol = localStorage.getItem('karaoke_volume');
    if (savedVol !== null) {
        player.volume = parseFloat(savedVol);
        document.getElementById('volumeSlider').value = savedVol;
        updateVolIcon();
    }
});

// เปลี่ยนระดับเสียงพร้อมบันทึกค่าลงเครื่อง
function changeVolume() {
    player.volume = document.getElementById('volumeSlider').value;
    localStorage.setItem('karaoke_volume', player.volume); // บันทึกค่า
    updateVolIcon();
}

// ระบบกดลำโพงเพื่อ Mute/Unmute
let lastVol = 1;
function toggleMute() {
    if (player.volume > 0) {
        lastVol = player.volume; // จำเสียงก่อนปิด
        player.volume = 0;
        document.getElementById('volumeSlider').value = 0;
    } else {
        player.volume = lastVol > 0 ? lastVol : 0.5; // คืนค่าเสียงเดิม
        document.getElementById('volumeSlider').value = player.volume;
    }
    localStorage.setItem('karaoke_volume', player.volume);
    updateVolIcon();
}

// อัปเดตไอคอนลำโพงตามระดับเสียง (ถ้าเสียงเป็น 0 ให้เป็นรูปกากบาท)
function updateVolIcon() {
    const volIcon = document.getElementById('volIcon');
    if (player.volume === 0) {
        volIcon.innerHTML = `<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line>`;
    } else {
        volIcon.innerHTML = `<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>`;
    }
}

// ระบบ Picture-in-Picture (จอเล็กแบบลอย)
async function togglePiP() {
    try {
        if (document.pictureInPictureElement) {
            await document.exitPictureInPicture();
        } else {
            await player.requestPictureInPicture();
        }
    } catch (error) { console.log("เบราว์เซอร์นี้ไม่รองรับ PiP"); }
}

function formatTitle(name) { return name ? name.replace('.mp4', '').replace(/_/g, ' ') : ""; }

const searchInput = document.getElementById('query');
searchInput.addEventListener('input', () => {
    clearTimeout(suggestTimeout);
    if (searchInput.value.trim().length < 1) { document.getElementById('suggestions').style.display = 'none'; return; }
    suggestTimeout = setTimeout(() => { searchSongs(); }, 500);
});

async function searchSongs() {
    const q = document.getElementById('query').value;
    if (!q) return;
    try {
        const res = await fetch(`/search?q=${encodeURIComponent(q)}`);
        const songs = await res.json();
        document.getElementById('searchResults').innerHTML = songs.map(s => {
            const safeTitle = s.title.replace(/'/g, "\\'").replace(/"/g, '&quot;');
            return `
            <div class="search-result-item" ondblclick="addSong('${s.url}', '${safeTitle}', this)">
                <div style="display: flex; gap: 12px; align-items: center; pointer-events: none;">
                    <img src="${s.thumbnail}" width="80" style="border-radius:8px; aspect-ratio:16/9; object-fit:cover;">
                    <div class="item-title" style="font-size: 13px; font-weight: 500; flex: 1; line-height:1.3;">${s.title}</div>
                </div>
            </div>`;
        }).join('');
    } catch (err) { }
}

async function addSong(url, title, element) {
    if (element) {
        element.style.transform = 'scale(0.95)';
        setTimeout(() => { element.style.transform = ''; }, 150);
        element.classList.add('added-blink');
        setTimeout(() => element.classList.remove('added-blink'), 400);
    }

    const newSong = { title: title, url: url, fileName: "", isReady: false };
    bookingQueue.push(newSong);
    renderQueue();

    setTimeout(() => { document.getElementById('readyQueue').scrollTo({ top: 9999, behavior: 'smooth' }); }, 50);

    if (currentIndex === -1) {
        currentIndex = bookingQueue.length - 1;
        document.getElementById('currentSongTitle').innerText = "⏳ รอโหลดไฟล์แป๊บนึงน้า...";
        renderQueue();
    }

    try {
        const res = await fetch(`/add_song?url=${encodeURIComponent(url)}&title=${encodeURIComponent(title)}`);
        const data = await res.json();

        const songIndex = bookingQueue.findIndex(s => s.url === url && !s.isReady);
        if (data.status === "success" && songIndex !== -1) {
            bookingQueue[songIndex].isReady = true;
            bookingQueue[songIndex].fileName = data.title + ".mp4";
            if (currentIndex === songIndex && player.paused) playAtIndex(currentIndex);
        } else if (songIndex !== -1) {
            removeSong({ stopPropagation: () => { } }, songIndex);
        }
    } catch (err) { }
}

function dragStart(event, index) { dragStartIndex = index; event.target.classList.add('dragging'); }
function dragEnd(event) { event.target.classList.remove('dragging'); document.querySelectorAll('.queue-item').forEach(item => item.classList.remove('drag-over')); }
function dragOver(event, element) { event.preventDefault(); event.dataTransfer.dropEffect = 'move'; element.classList.add('drag-over'); }
function dragLeave(event, element) { element.classList.remove('drag-over'); }
function drop(event, dropIndex) {
    event.preventDefault(); document.querySelectorAll('.queue-item').forEach(item => item.classList.remove('drag-over'));
    if (dragStartIndex === dropIndex || dragStartIndex === -1) return;
    const draggedSong = bookingQueue[dragStartIndex];
    bookingQueue.splice(dragStartIndex, 1); bookingQueue.splice(dropIndex, 0, draggedSong);
    if (currentIndex === dragStartIndex) { currentIndex = dropIndex; } else if (dragStartIndex < currentIndex && dropIndex >= currentIndex) { currentIndex--; } else if (dragStartIndex > currentIndex && dropIndex <= currentIndex) { currentIndex++; }
    renderQueue();
}

function removeSong(event, index) {
    if (event && event.stopPropagation) event.stopPropagation();
    if (index === currentIndex) {
        player.pause(); player.removeAttribute('src');
        player.style.aspectRatio = ''; // คืนร่างเดิมตอนกดลบเพลง
        document.getElementById('currentSongTitle').innerText = "เพลย์ลิสต์ที่ดีที่สุด"; currentIndex = -1;
        document.documentElement.style.setProperty('--theme-rgb', '0, 113, 227');
    } else if (index < currentIndex) { currentIndex--; }
    bookingQueue.splice(index, 1); renderQueue();
}

function updateUpNext() {
    const upNextElem = document.getElementById('upNextDisplay');
    let newText = `ถัดไป: -`;
    if (currentIndex !== -1 && currentIndex + 1 < bookingQueue.length) {
        const nextSong = bookingQueue[currentIndex + 1];
        const displayTitle = typeof nextSong === 'string' ? nextSong : nextSong.title;
        newText = `ถัดไป: ${formatTitle(displayTitle)}`;
    }
    if (upNextElem.innerText !== newText) {
        upNextElem.classList.remove('show');
        setTimeout(() => { upNextElem.innerText = newText; upNextElem.classList.add('show'); }, 400);
    } else { upNextElem.classList.add('show'); }
}

function renderQueue() {
    let html = '';
    bookingQueue.forEach((song, index) => {
        const isPlaying = index === currentIndex;
        const indexDisplay = isPlaying ? `<div class="eq-bars"><div class="eq-bar"></div><div class="eq-bar"></div><div class="eq-bar"></div></div>` : index + 1;
        const displayTitle = typeof song === 'string' ? song : song.title;

        html += `
            <div class="queue-item ${isPlaying ? 'playing' : ''}" draggable="true" 
                 ondragstart="dragStart(event, ${index})" ondragend="dragEnd(event)"
                 ondragover="dragOver(event, this)" ondragleave="dragLeave(event, this)"
                 ondrop="drop(event, ${index})" onclick="playAtIndex(${index})">
                <div class="drag-handle">☰</div>
                <div style="color:#ffffff; font-weight:600; min-width:20px; display:flex; justify-content:center;">${indexDisplay}</div>
                <div class="queue-name">${formatTitle(displayTitle)}</div>
                <button class="btn-remove" onclick="removeSong(event, ${index})" title="ลบออกจากคิว">✕</button>
            </div>`;
    });
    document.getElementById('readyQueue').innerHTML = html || '<p style="color:#86868b; text-align:center; font-weight:400; font-size:13px;">ยังไม่มีเพลงในคิวจ้า</p>';
    updateUpNext();
}

// function playNext() { if (currentIndex + 1 < bookingQueue.length) playAtIndex(currentIndex + 1); }
// function playPrevious() { if (currentIndex - 1 >= 0) playAtIndex(currentIndex - 1); else if (currentIndex === 0) { player.currentTime = 0; player.play(); } }
/* =========================================
   🎛️ [Premium Audio] ระบบสมูทเฟด (Fade In / Out) ทุกกรณี
   ========================================= */
function playNext() {
    if (currentIndex + 1 < bookingQueue.length) {
        playAtIndex(currentIndex + 1);
    } else if (isAutoPlayEnabled) {
        preloadNextAutoSong();
    }
}

function playPrevious() {
    if (player.currentTime > 3) {
        // 🎯 ถ้าร้องไปแล้วเกิน 3 วิ ให้เฟดเสียงออก แล้วกรอกลับไปเริ่มเพลงเดิมใหม่
        fadeAndRestartCurrent();
    } else if (currentIndex - 1 >= 0) {
        playAtIndex(currentIndex - 1);
    }
}

// ฟังก์ชันพิเศษ: เฟดเสียงและกรอกลับไปเริ่มเพลงเดิม
function fadeAndRestartCurrent() {
    if (player.isFading) return;
    player.isFading = true;
    let vol = player.volume;
    const targetVol = parseFloat(document.getElementById('volumeSlider').value);

    const fadeOut = setInterval(() => {
        vol -= 0.05;
        if (vol <= 0) {
            player.volume = 0;
            clearInterval(fadeOut);
            animateProgressBack(); // เรียกแอนิเมชันรูดหลอดเวลา

            // เฟดอินกลับมา
            const fadeIn = setInterval(() => {
                vol += 0.05;
                if (vol >= targetVol) {
                    player.volume = targetVol;
                    clearInterval(fadeIn);
                    player.isFading = false;
                } else {
                    player.volume = vol;
                }
            }, 40);
        } else {
            player.volume = vol;
        }
    }, 30);
}

// 🎯 ฟังก์ชันสั่งเปลี่ยนเพลงข้ามคิว (มี Fade-out)
async function playAtIndex(index) {
    if (index < 0 || index >= bookingQueue.length) return;

    // ล็อกปุ่มไว้ ป้องกันกดรัวๆ
    if (player.isFading) return;

    if (!player.paused && player.volume > 0) {
        player.isFading = true;
        let vol = player.volume;

        // เฟดเอาต์: ค่อยๆ ลดเสียงลงทีละนิด (ใช้เวลาประมาณ 0.8 วินาทีให้สมูทสุดๆ)
        const fadeOut = setInterval(() => {
            vol -= 0.05;
            if (vol <= 0) {
                player.volume = 0;
                clearInterval(fadeOut);
                player.isFading = false;
                executePlay(index); // พอเสียงเงียบสนิท ค่อยเริ่มเพลงใหม่
            } else {
                player.volume = vol;
            }
        }, 30);
    } else {
        executePlay(index);
    }
}

// 🎯 ฟังก์ชันเริ่มเพลงใหม่ (มี Fade-in)
// function executePlay(index) {
//     animateProgressBack();

//     currentIndex = index;
//     const song = bookingQueue[index];
//     const isStr = typeof song === 'string';
//     const displayTitle = isStr ? song : song.title;
//     const filename = isStr ? song : song.fileName;

//     if (isStr || song.isReady) {
//         player.src = `/songs/${encodeURIComponent(filename)}`;
//         document.getElementById('currentSongTitle').innerText = formatTitle(displayTitle);

//         // ดึงระดับเสียงเป้าหมายที่ตั้งไว้ในหลอด
//         const targetVol = parseFloat(document.getElementById('volumeSlider').value);
//         player.volume = 0; // เริ่มจากเงียบสนิท
//         player.play().catch(e => console.log("รอไฟล์มาเต็มๆ"));

//         // เฟดอิน: ค่อยๆ ดังขึ้น
//         player.isFading = true;
//         let vol = 0;
//         const fadeIn = setInterval(() => {
//             vol += 0.05;
//             if (vol >= targetVol) {
//                 player.volume = targetVol;
//                 clearInterval(fadeIn);
//                 player.isFading = false;
//             } else {
//                 player.volume = vol;
//             }
//         }, 40); 

//     } else {
//         player.pause(); player.removeAttribute('src'); player.load(); 
//         player.style.aspectRatio = ''; 
//         document.getElementById('currentSongTitle').innerText = "⏳ รอโหลดไฟล์แป๊บนึงน้า...";
//     }
//     renderQueue(); 
// }

// 🎯 ฟังก์ชันเริ่มเล่นเพลงใหม่ (พร้อมระบบ Fade-in และนักสืบหาปก)
function executePlay(index) {
    animateProgressBack();

    currentIndex = index;
    const song = bookingQueue[index];
    const isStr = typeof song === 'string';
    const displayTitle = isStr ? song : song.title;
    const filename = isStr ? song : song.fileName;

    // 🔥 [AI นักสืบหาปก] ตรวจสอบว่าเพลงนี้มีรูปปกหรือยัง?
    if (song && !song.thumb) {
        if (song.url) {
            // ถ้าเป็นเพลงใหม่เพิ่งกดเพิ่ม คราฟต์ปกจาก URL ได้เลย
            const match = song.url.match(/v=([^&]+)/);
            if (match) song.thumb = `https://i.ytimg.com/vi/${match[1]}/hqdefault.jpg`;
        } else {
            // ถ้าเป็นเพลงเก่าในเครื่อง ให้แอบยิง API ไปสืบหาปกมาจาก YouTube!
            fetch(`/search?q=${encodeURIComponent(displayTitle)}`)
                .then(res => res.json())
                .then(data => {
                    if (data && data.length > 0 && data[0].thumbnail) {
                        song.thumb = data[0].thumbnail; // แปะรูปลงไปในคิว
                    }
                }).catch(() => { });
        }
    }

    if (isStr || song.isReady) {
        player.src = `/songs/${encodeURIComponent(filename)}`;
        document.getElementById('currentSongTitle').innerText = formatTitle(displayTitle);

        const targetVol = parseFloat(document.getElementById('volumeSlider').value);
        player.volume = 0;
        player.play().catch(e => console.log("รอไฟล์มาเต็มๆ"));

        player.isFading = true;
        let vol = 0;
        const fadeIn = setInterval(() => {
            vol = Math.min(targetVol, vol + 0.05);
            player.volume = vol;
            if (vol >= targetVol) {
                clearInterval(fadeIn);
                player.isFading = false;
            }
        }, 40);

    } else {
        player.pause(); player.removeAttribute('src'); player.load();
        player.style.aspectRatio = '';
        document.getElementById('currentSongTitle').innerText = "⏳ รอโหลดไฟล์แป๊บนึงน้า...";
    }
    renderQueue();
}

// async function playAtIndex(index) {
//     if (index < 0 || index >= bookingQueue.length) return;
//     if(!player.paused && player.volume > 0) {
//         let vol = player.volume;
//         const fade = setInterval(() => {
//             vol = Math.max(0, vol - 0.1); player.volume = vol;
//             if(vol <= 0) { clearInterval(fade); executePlay(index); }
//         }, 50);
//     } else { executePlay(index); }
// }
// 🎯 ฟังก์ชันสั่งเปลี่ยนเพลง (พร้อมระบบ Fade-out)
async function playAtIndex(index) {
    if (index < 0 || index >= bookingQueue.length) return;

    // ล็อกปุ่มไว้ชั่วคราว ป้องกันการกดเปลี่ยนเพลงรัวๆ จนเบราว์เซอร์เอ๋อ
    if (player.isFading) return;

    if (!player.paused && player.volume > 0) {
        player.isFading = true; // เปิดล็อก
        let vol = player.volume;
        // ค่อยๆ ลดเสียงลงทีละ 0.05 ทุกๆ 30 มิลลิวินาที (นุ่มนวลกว่าเดิม)
        const fadeOut = setInterval(() => {
            vol = Math.max(0, vol - 0.05);
            player.volume = vol;
            if (vol <= 0) {
                clearInterval(fadeOut);
                player.isFading = false; // ปลดล็อก
                executePlay(index); // พอเสียงเงียบสนิท ค่อยเรียกเพลงใหม่มาเล่น
            }
        }, 30);
    } else {
        executePlay(index);
    }
}

// 🎯 ฟังก์ชันรูดหลอดเวลากลับไปที่ 0 อย่างสมูท (Rewind Animation)
function animateProgressBack() {
    isDraggingProgress = true; // ปิดการอัปเดตเวลาจากวิดีโอชั่วคราว
    let currentVal = parseFloat(progressBar.value);

    // ถ้าอยู่ที่ 0 อยู่แล้ว ไม่ต้องรูด
    if (currentVal <= 0) {
        isDraggingProgress = false;
        return;
    }

    const step = currentVal / 20; // แบ่งการรูดเป็น 20 เฟรม ให้ดูสมูท
    const slideBack = setInterval(() => {
        currentVal -= step;
        if (currentVal <= 0) {
            progressBar.value = 0;
            currentTimeEl.innerText = "0:00"; // รีเซ็ตตัวเลขเวลา
            clearInterval(slideBack);
            isDraggingProgress = false; // คืนการควบคุมให้วิดีโอ
        } else {
            progressBar.value = currentVal;
        }
    }, 15); // รันทุก 15ms (ลื่นปรื๊ดแน่นอน)
}

// 🎯 ฟังก์ชันเริ่มเล่นเพลงใหม่ (พร้อมระบบ Fade-in)
function executePlay(index) {
    // รูดหลอดเวลากลับไปที่ 0 อย่างสมูท
    animateProgressBack();

    currentIndex = index;
    const song = bookingQueue[index];
    const isStr = typeof song === 'string';
    const displayTitle = isStr ? song : song.title;
    const filename = isStr ? song : song.fileName;

    if (isStr || song.isReady) {
        player.src = `/songs/${encodeURIComponent(filename)}`;
        document.getElementById('currentSongTitle').innerText = formatTitle(displayTitle);

        // 🔥 ไม้ตาย Fade-in: ลบ changeVolume() เดิมทิ้ง แล้วใช้การไต่ระดับเสียงแทน
        const targetVol = parseFloat(document.getElementById('volumeSlider').value);
        player.volume = 0; // บังคับให้เริ่มที่เสียง 0 (เงียบสนิท)
        player.play().catch(e => console.log("รอไฟล์มาเต็มๆ"));

        // ค่อยๆ เร่งเสียงขึ้นไปหาเป้าหมาย (targetVol) ทีละ 0.05
        player.isFading = true;
        let vol = 0;
        const fadeIn = setInterval(() => {
            vol = Math.min(targetVol, vol + 0.05);
            player.volume = vol;
            if (vol >= targetVol) {
                clearInterval(fadeIn);
                player.isFading = false; // ปลดล็อก
            }
        }, 40); // ค่อยๆ ดังขึ้น นุ่มๆ ฟินๆ

    } else {
        player.pause(); player.removeAttribute('src'); player.load();
        player.style.aspectRatio = '';
        document.getElementById('currentSongTitle').innerText = "⏳ รอโหลดไฟล์แป๊บนึงน้า...";
    }
    renderQueue();
}

player.onplay = () => {
    document.getElementById('playPauseBtn').innerHTML = `<svg class="svg-icon-large" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>`;
    resetIdleTimer();
};
player.onpause = () => {
    document.getElementById('playPauseBtn').innerHTML = `<svg class="svg-icon-large" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>`;
    document.body.classList.remove('idle-mode');
    clearTimeout(idleTimer);
};
player.onended = () => playNext();

async function initQueue() {
    try {
        const res = await fetch('/list_downloads');
        const files = await res.json();
        bookingQueue = files.map(f => ({ title: formatTitle(f), fileName: f, isReady: true, url: "" }));
        renderQueue();
    } catch (err) { }
}
initQueue();
/* 🎯 4. ระบบ Media Session API (เชื่อมต่อกับ Control Center ของเครื่อง) และเปลี่ยนชื่อแท็บ */
function setupMediaSession(title) {
    if ('mediaSession' in navigator) {
        navigator.mediaSession.metadata = new MediaMetadata({
            title: title,
            artist: 'Karaoke Studio Space',
            artwork: [
                { src: 'https://cdn-icons-png.flaticon.com/512/3048/3048122.png', sizes: '512x512', type: 'image/png' }
            ]
        });
        navigator.mediaSession.setActionHandler('play', togglePlay);
        navigator.mediaSession.setActionHandler('pause', togglePlay);
        navigator.mediaSession.setActionHandler('previoustrack', playPrevious);
        navigator.mediaSession.setActionHandler('nexttrack', playNext);
    }
}

// แอบเปลี่ยนชื่อแท็บเบราว์เซอร์และอัปเดตระบบหลังบ้านเรื่อยๆ
setInterval(() => {
    const currentTitle = document.getElementById('currentSongTitle').innerText;

    // เปลี่ยนชื่อแท็บแบบคลีนๆ ไม่มีอีโมจิรกๆ
    if (currentTitle !== "เพลย์ลิสต์ที่ดีที่สุด" && currentTitle !== "⏳ รอโหลดไฟล์แป๊บนึงน้า...") {
        document.title = currentTitle; // 🔥 โชว์แค่ชื่อเพลงเพียวๆ ดูแพงกว่า
        setupMediaSession(currentTitle); // ส่งชื่อเพลงไปให้ Control Center
    } else {
        document.title = "Music Studio - Space";
    }
}, 1000);
/* =========================================
   ✨ [Premium Favicon] แท่งเสียงขยับได้บนแท็บเบราว์เซอร์
   ========================================= */
const favCanvas = document.createElement('canvas');
favCanvas.width = 32;
favCanvas.height = 32;
const favCtx = favCanvas.getContext('2d');

// หาแท็ก <link rel="icon"> ใน Head ถ้าไม่มีให้สร้างใหม่
let favLink = document.querySelector("link[rel~='icon']");
if (!favLink) {
    favLink = document.createElement('link');
    favLink.rel = 'icon';
    document.head.appendChild(favLink);
}

function updateFavicon() {
    // ล้างภาพเก่าออกก่อนวาดใหม่
    favCtx.clearRect(0, 0, 32, 32);

    // ดึงสี Dynamic Theme ปัจจุบันมาใช้วาด (ถ้าไม่มีใช้สีขาว)
    const rgbStr = document.documentElement.style.getPropertyValue('--theme-rgb') || '255, 255, 255';
    favCtx.fillStyle = `rgb(${rgbStr})`;

    if (player && !player.paused && player.src) {
        // 🎵 โหมดกำลังเล่น: สุ่มความสูงของแท่งเสียงให้ดูเหมือนเต้นตามเพลง
        const h1 = 12 + Math.random() * 20;
        const h2 = 12 + Math.random() * 20;
        const h3 = 12 + Math.random() * 20;

        favCtx.beginPath();
        favCtx.roundRect(4, 32 - h1, 6, h1, 2);  // แท่งซ้าย
        favCtx.roundRect(13, 32 - h2, 6, h2, 2); // แท่งกลาง
        favCtx.roundRect(22, 32 - h3, 6, h3, 2); // แท่งขวา
        favCtx.fill();
    } else {
        // ⏸️ โหมดหยุดเล่น/ยังไม่เลือกเพลง: แท่งเสียงหยุดนิ่งเป็นระเบียบ
        favCtx.beginPath();
        favCtx.roundRect(4, 24, 6, 8, 2);
        favCtx.roundRect(13, 16, 6, 16, 2);
        favCtx.roundRect(22, 20, 6, 12, 2);
        favCtx.fill();
    }

    // แปลงภาพที่วาดเสร็จเป็นไฟล์ PNG แล้วส่งไปอัปเดตบนแท็บเบราว์เซอร์
    favLink.href = favCanvas.toDataURL('image/png');
}

// สั่งให้วาดภาพใหม่ทุกๆ 0.25 วินาที (4 FPS ให้พอดุ๊กดิ๊กกำลังสวย ไม่กินสเปคคอม)
setInterval(updateFavicon, 250);
// /* =========================================
//    ✨ [ระบบหลอดเวลาเพลง (Progress Bar)]
//    ========================================= */
// // 🎯 [ระบบหลอดเวลาเพลง]
// const progressBar = document.getElementById('progressBar');
// const currentTimeEl = document.getElementById('currentTime');
// const durationTimeEl = document.getElementById('durationTime');
// let isDraggingProgress = false;

// function formatTime(seconds) {
//     if (isNaN(seconds)) return "0:00";
//     const m = Math.floor(seconds / 60);
//     const s = Math.floor(seconds % 60);
//     return `${m}:${s < 10 ? '0' : ''}${s}`;
// }

// // // อัปเดตเวลาตามวิดีโอ (และฝังระบบแอบโหลดเพลงล่วงหน้า)
// // player.addEventListener('timeupdate', () => {
// //     if (!isDraggingProgress && player.duration) {
// //         progressBar.value = (player.currentTime / player.duration) * 100;
// //         currentTimeEl.innerText = formatTime(player.currentTime);
// //         durationTimeEl.innerText = formatTime(player.duration);

// //         // 🔥 [ฟีเจอร์ใหม่: Pre-load] ถ้าระบบออโต้รันเปิดอยู่ และกำลังเล่นเพลงสุดท้ายในคิว
// //         if (isAutoPlayEnabled && currentIndex === bookingQueue.length - 1 && !isFetchingAutoPlay) {
// //             const timeRemaining = player.duration - player.currentTime;
// //             // ถ้าเพลงเล่นมาเกินครึ่งทางแล้ว หรือเหลือเวลาอีกแค่ 30 วินาที ให้สั่งหาเพลงถัดไปมารอเลย!
// //             if (timeRemaining < 30 || player.currentTime > player.duration / 2) {
// //                 preloadNextAutoSong();
// //             }
// //         }
// //     }
// // });
// // อัปเดตเวลาตามวิดีโอ (คืนค่ากลับเป็นปกติ)
// player.addEventListener('timeupdate', () => {
//     if (!isDraggingProgress && player.duration) {
//         progressBar.value = (player.currentTime / player.duration) * 100;
//         currentTimeEl.innerText = formatTime(player.currentTime);
//         durationTimeEl.innerText = formatTime(player.duration);
//     }
//     // 🔥 ระบบวิ่งเนื้อเพลงตามเวลาจริง
//         if (document.body.classList.contains('lyrics-active') && currentLyrics.length > 0) {
//             const currentTime = player.currentTime;
//             let activeIdx = -1;

//             // หาว่าตอนนี้ร้องถึงบรรทัดไหนแล้ว
//             for (let i = 0; i < currentLyrics.length; i++) {
//                 if (currentTime >= currentLyrics[i].time) { activeIdx = i; } 
//                 else { break; }
//             }

//             if (activeIdx !== -1 && activeIdx !== lastLyricIndex) {
//                 const oldActive = document.querySelector('.lyric-line.active');
//                 if (oldActive) oldActive.classList.remove('active');

//                 const newActive = document.getElementById(`lyric-${activeIdx}`);
//                 if (newActive) {
//                     newActive.classList.add('active');
//                     // เลื่อนให้บรรทัดที่ร้องอยู่เด้งมาตรงกลางจอเสมอ แบบนุ่มๆ
//                     newActive.scrollIntoView({ behavior: 'smooth', block: 'center' });
//                 }
//                 lastLyricIndex = activeIdx;
//             }
//         }
// });

// // ตอนผู้ใช้กำลังลากหลอดเวลา
// progressBar.addEventListener('input', () => {
//     isDraggingProgress = true;
//     if(player.duration) currentTimeEl.innerText = formatTime((progressBar.value / 100) * player.duration);
// });

// // ปล่อยเมาส์ปุ๊บ กรอเพลงปั๊บ
// progressBar.addEventListener('change', () => {
//     if(player.duration) player.currentTime = (progressBar.value / 100) * player.duration;
//     isDraggingProgress = false;
// });

// /* =========================================
//    🖥️ [App Mode] ระบบขยายเต็มจอ (Fullscreen)
//    ========================================= */
// // 🔥 1. สร้างฟังก์ชันกลาง เพื่อให้ปุ่ม F และปุ่มบนจอเรียกใช้งานได้
// function toggleFullScreen() {
//     if (!document.fullscreenElement) {
//         document.documentElement.requestFullscreen().catch(err => {
//             console.log("ไม่สามารถขยายเต็มจอได้:", err);
//         });
//     } else {
//         if (document.exitFullscreen) {
//             document.exitFullscreen();
//         }
//     }
// }

// // 🔥 2. ดับเบิ้ลคลิกเพื่อขยายเต็มจอ (ดึงฟังก์ชันด้านบนมาใช้งาน)
// document.addEventListener('dblclick', (e) => {
//     const isInteractive = e.target.closest('button') || 
//                           e.target.closest('input') || 
//                           e.target.closest('.search-result-item') || 
//                           e.target.closest('.queue-item') ||
//                           e.target.closest('.premium-control-bar') ||
//                           e.target.closest('.progress-container');

//     if (isInteractive) return; 

//     toggleFullScreen(); // เรียกใช้ฟังก์ชันสลับจอ
// });
// /* =========================================
//    ♾️ [Endless Radio] ระบบเล่นเพลงอัตโนมัติ (Watchdog AI)
//    ========================================= */
// let isAutoPlayEnabled = false;
// let isFetchingAutoPlay = false; 

// function toggleAutoPlay() {
//     isAutoPlayEnabled = !isAutoPlayEnabled;
//     const btn = document.getElementById('autoPlayBtn');
//     if (isAutoPlayEnabled) {
//         btn.classList.add('active-autoplay');
//         // ถ้าคิวว่างพอดี ก็พุ่งไปหาเพลงเลย
//         if (currentIndex === bookingQueue.length - 1) {
//             preloadNextAutoSong();
//         }
//     } else {
//         btn.classList.remove('active-autoplay');
//     }
// }

// function playNext() { 
//     if (currentIndex + 1 < bookingQueue.length) {
//         playAtIndex(currentIndex + 1); 
//     } else if (isAutoPlayEnabled) {
//         preloadNextAutoSong();
//     }
// }

// // 🎯 สายลับเฝ้าคิว: ตรวจทุก 2 วินาที (แยกการทำงานออกมา ไม่ต้องพึ่งวิดีโอ)
// setInterval(() => {
//     if (isAutoPlayEnabled && bookingQueue.length > 0) {
//         // ถ้ากำลังเล่นเพลงสุดท้ายในคิว และไม่ได้กำลังควานหาเพลงอยู่
//         if (currentIndex === bookingQueue.length - 1 && !isFetchingAutoPlay) {
//             preloadNextAutoSong();
//         }
//     }
// }, 2000);

// // ฟังก์ชันสายลับเฝ้าคิว (เวอร์ชันฉลาดขั้นสุด ตัดเพลงซ้ำ + สุ่มกว้างขึ้น)
// async function preloadNextAutoSong() {
//     if (isFetchingAutoPlay) return;
//     isFetchingAutoPlay = true;

//     const currentSong = bookingQueue[currentIndex];
//     if (!currentSong) { isFetchingAutoPlay = false; return; }

//     const title = typeof currentSong === 'string' ? currentSong : currentSong.title;

//     // 1. อัปเกรดการค้นหา: สุ่มคำสร้อยต่อท้าย เพื่อให้ผลลัพธ์ไม่ซ้ำซาก
//     let query = title;
//     if (title.includes('-')) {
//         const artist = title.split('-')[0].trim();
//         const randomSuffix = ["official", "playlist", "hits", "live"][Math.floor(Math.random() * 4)];
//         query = `${artist} ${randomSuffix}`; 
//     } else {
//         query = title + " song";
//     }

//     try {
//         const res = await fetch(`/search?q=${encodeURIComponent(query)}`);
//         const songs = await res.json();

//         // 🔥 2. ฟังก์ชันทำความสะอาดชื่อเพลง (ตัดวงเล็บคำว่า Official, Lyrics, MV ทิ้งให้หมด)
//         const cleanTitle = (t) => t.toLowerCase().replace(/\[.*?\]|\(.*?\)|official|video|audio|lyrics|mv|hd/g, '').trim();

//         // 🔥 3. กรองเพลงซ้ำแบบฉลาด (เช็คทั้ง URL และ ชื่อเพลงที่ตัดคำสร้อยแล้ว)
//         const newSongs = songs.filter(s => {
//             const sClean = cleanTitle(s.title);
//             return !bookingQueue.some(q => {
//                 const qTitle = typeof q === 'string' ? q : q.title;
//                 // ถ้า URL ตรงกัน หรือ ชื่อเพลงคล้ายกันเกินไป = ถือว่าซ้ำ! ตัดทิ้ง!
//                 return q.url === s.url || cleanTitle(qTitle) === sClean;
//             });
//         });

//         if (newSongs.length > 0) {
//             // 4. ขยายวงสุ่มเป็น 8 อันดับแรก (จากเดิม 4) เพื่อให้เจอเพลงหลากหลายขึ้น
//             const randomIndex = Math.floor(Math.random() * Math.min(8, newSongs.length));
//             const nextSong = newSongs[randomIndex];

//             // แอบโยนเพลงใส่คิวทันที
//             addSong(nextSong.url, nextSong.title, null);
//         } else {
//             console.log("Endless Radio: เพลงเซ็ตนี้ซ้ำหมดแล้ว เดี๋ยวรอบหน้าสุ่มหาใหม่");
//         }
//     } catch(e) {
//         console.log("AutoPlay Error:", e);
//     } finally {
//         setTimeout(() => { isFetchingAutoPlay = false; }, 2000);
//     }
// }
// /* =========================================
//    👁️ [Focus Mode] ซ่อนแถบซ้ายเมื่อคลิกพื้นที่ว่าง
//    ========================================= */
// document.addEventListener('click', (e) => {
//     // 🔥 รายชื่อสิ่งของที่ "ห้ามคลิก" แล้วพับจอ (ถ้าคลิกโดนพวกนี้ให้ข้ามไป)
//     const isInteractive = e.target.closest('button') || 
//                           e.target.closest('input') || 
//                           e.target.closest('.search-result-item') || 
//                           e.target.closest('.queue-item') ||
//                           e.target.closest('.premium-control-bar') ||
//                           e.target.closest('.progress-container') ||
//                           e.target.closest('.sidebar-left') || // คลิกในแถบซ้ายจะไม่พับ
//                           e.target.closest('.sidebar-right') || // คลิกในคิวเพลงขวาจะไม่พับ
//                           e.target.closest('video'); // คลิกที่ตัววิดีโอก็จะไม่พับ

//     // ถ้าเผลอไปกดโดนของพวกนี้ ให้หยุดการทำงาน (ไม่ต้องพับจอ)
//     if (isInteractive) return; 

//     // ถ้ากดโดน "พื้นที่ว่าง" จริงๆ (เช่น พื้นหลัง, หรือขอบๆ จอ) ให้สลับโหมดพับ/กาง แถบซ้าย
//     document.body.classList.toggle('collapse-left');
// });
// /* =========================================
//    🎤 [Lyrics API] ค้นหาและซิงค์เนื้อเพลง
//    ========================================= */
// let currentLyrics = [];
// let lastLyricIndex = -1;

// // ฟังก์ชันสลับโหมดเนื้อเพลง (อัปเดตปุ่มให้สว่างขึ้นด้วย)
// function toggleLyrics() {
//     document.body.classList.toggle('lyrics-active');

//     // ดึงปุ่มไมค์มาสลับแสงสว่าง
//     const lyricsBtn = document.getElementById('lyricsBtn');

//     if (document.body.classList.contains('lyrics-active')) {
//         if (lyricsBtn) lyricsBtn.classList.add('active-lyrics'); // เปิดไฟปุ่ม
//         fetchLyricsForCurrentSong(); // สั่งดึงเนื้อเพลง
//     } else {
//         if (lyricsBtn) lyricsBtn.classList.remove('active-lyrics'); // ปิดไฟปุ่ม
//     }
// }

// // ฟังก์ชันดึงเนื้อเพลง (เวอร์ชันกรองคำมั่ว/จับผิด API)
// async function fetchLyricsForCurrentSong() {
//     const titleEl = document.getElementById('currentSongTitle').innerText;
//     const lyricsContent = document.getElementById('lyricsContent');
//     if (titleEl === "เพลย์ลิสต์ที่ดีที่สุด" || titleEl.includes("⏳")) return;

//     lyricsContent.innerHTML = `<div class="lyric-line active">กำลังค้นหาเนื้อเพลง...</div>`;
//     currentLyrics = [];
//     lastLyricIndex = -1;

//     // 1. ทำความสะอาดชื่อเพลง (ตัดวงเล็บ official, audio ทิ้ง)
//     let cleanTitle = titleEl.replace(/\[.*?\]|\(.*?\)|official|video|audio|mv|lyrics/gi, '').trim();

//     // 2. พยายามดึง "ชื่อเพลงเพียวๆ" ออกมาเช็ค (กรณีที่ชื่อเป็น Artist - Song)
//     let coreTrackName = cleanTitle;
//     if (cleanTitle.includes('-')) {
//         const parts = cleanTitle.split('-');
//         coreTrackName = parts[parts.length - 1].trim(); // มักจะอยู่ก้อนหลังสุด
//     }

//     try {
//         // ยิง API ค้นหา
//         const res = await fetch(`https://lrclib.net/api/search?q=${encodeURIComponent(cleanTitle)}`);
//         const data = await res.json();

//         // 🔥 3. ระบบตรวจคนเข้าเมือง: กรองแบบเข้มงวด ป้องกัน API ยัดไส้เพลงอื่นมาให้
//         const trackWithLyrics = data.find(t => {
//             if (!t.syncedLyrics) return false; // ต้องมีเนื้อเพลงแบบซิงค์เวลา

//             const apiTrackName = t.trackName.toLowerCase();
//             const myTrackName = coreTrackName.toLowerCase();
//             const fullTitle = cleanTitle.toLowerCase();

//             // กฎเหล็ก: ชื่อเพลงที่ API ส่งมา ต้องมีส่วนคล้ายกับชื่อเพลงของเรา
//             return apiTrackName.includes(myTrackName) || 
//                    myTrackName.includes(apiTrackName) || 
//                    fullTitle.includes(apiTrackName);
//         });

//         if (trackWithLyrics) {
//             parseLyrics(trackWithLyrics.syncedLyrics);
//         } else {
//             // ถ้าหาไม่เจอ หรือเจอแต่เพลงไม่ตรงกัน ให้โชว์ข้อความนี้แทน
//             lyricsContent.innerHTML = `<div class="lyric-line" style="filter: blur(0); color: rgba(255,255,255,0.5); font-size: 24px; transform: scale(1);">ยังไม่มีเนื้อเพลง...</div>`;
//         }
//     } catch (err) {
//         lyricsContent.innerHTML = `<div class="lyric-line">เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์เนื้อเพลง</div>`;
//     }
// }

// // ถอดรหัสเวลาจากไฟล์ LRC มาเป็นวินาทีให้วิดีโอเข้าใจ
// function parseLyrics(lrcString) {
//     const lines = lrcString.split('\n');
//     currentLyrics = [];
//     const regex = /\[(\d{2}):(\d{2}\.\d{2,3})\](.*)/; // แปลง [01:23.45] text

//     let html = '';
//     lines.forEach((line) => {
//         const match = line.match(regex);
//         if (match) {
//             const mins = parseInt(match[1]);
//             const secs = parseFloat(match[2]);
//             const text = match[3].trim();
//             if (text) {
//                 const time = mins * 60 + secs;
//                 // ถ้าจิ้มที่เนื้อเพลง ให้กรอวิดีโอไปเวลานั้นเลย! (seekToLyric)
//                 html += `<div class="lyric-line" id="lyric-${currentLyrics.length}" onclick="if(player.duration) player.currentTime = ${time};">${text}</div>`;
//                 currentLyrics.push({ time, text });
//             }
//         }
//     });

//     document.getElementById('lyricsContent').innerHTML = html || `<div class="lyric-line">อ่านเนื้อเพลงไม่ได้</div>`;
// }
// // 🔥 บังคับให้เลื่อนมาตรงกลางแบบนุ่มนวล
// activeLine.scrollIntoView({ behavior: 'smooth', block: 'center' });

// // 🔥 ดักตอนเปลี่ยนเพลง: ถ้าเปิดโหมด L ค้างไว้ ให้ดึงเนื้อเพลงใหม่ทันที
// const originalExecutePlay = executePlay;
// executePlay = function(index) {
//     originalExecutePlay(index);
//     if (document.body.classList.contains('lyrics-active')) {
//         setTimeout(fetchLyricsForCurrentSong, 1500); // ดีเลย์นิดนึงรอชื่อเพลงอัปเดต
//     }
// };



/* =========================================
   ✨ [ระบบหลอดเวลาเพลง (Progress Bar)]
   ========================================= */
const progressBar = document.getElementById('progressBar');
const currentTimeEl = document.getElementById('currentTime');
const durationTimeEl = document.getElementById('durationTime');
let isDraggingProgress = false;

// 🔥 1. เครื่องยนต์สไลด์แบบสมูท (Premium Slide)
let isSliderAnimating = false;

function smoothSeekTo(targetTime) {
    if (!player.duration) return;
    const startPercent = parseFloat(progressBar.value);
    const endPercent = (targetTime / player.duration) * 100;
    const duration = 400; // ความเร็วในการสไลด์ 0.4 วิ (นุ่มๆ กำลังสวย)
    const startTime = performance.now();

    isSliderAnimating = true; // ล็อกหลอดเวลา
    player.currentTime = targetTime; // สั่งเพลงให้เล่นท่อนนั้นทันที จะได้ไม่ดีเลย์

    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOutQuart = 1 - Math.pow(1 - progress, 4); // สูตรหน่วงตอนจบแบบ Apple
        const currentPercent = startPercent + (endPercent - startPercent) * easeOutQuart;

        progressBar.value = currentPercent;
        progressBar.dispatchEvent(new Event('input'));

        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            isSliderAnimating = false; // สไลด์เสร็จ ปลดล็อก
        }
    }
    requestAnimationFrame(animate);
}

function formatTime(seconds) {
    if (isNaN(seconds)) return "0:00";
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
}

// อัปเดตเวลาตามวิดีโอ (คืนค่ากลับเป็นปกติ)
player.addEventListener('timeupdate', () => {
    // 🔥 2. ล็อกหลอดเวลาเวลาสไลด์
    if (!isDraggingProgress && !isSliderAnimating && player.duration) {
        progressBar.value = (player.currentTime / player.duration) * 100;
        currentTimeEl.innerText = formatTime(player.currentTime);
        durationTimeEl.innerText = formatTime(player.duration);
    }

    // ระบบวิ่งเนื้อเพลงตามเวลาจริง
    if (document.body.classList.contains('lyrics-active') && currentLyrics.length > 0) {
        const currentTime = player.currentTime;
        let activeIdx = -1;

        // หาว่าตอนนี้ร้องถึงบรรทัดไหนแล้ว
        for (let i = 0; i < currentLyrics.length; i++) {
            if (currentTime >= currentLyrics[i].time) { activeIdx = i; }
            else { break; }
        }

        if (activeIdx !== -1 && activeIdx !== lastLyricIndex) {
            const oldActive = document.querySelector('.lyric-line.active');
            if (oldActive) oldActive.classList.remove('active');

            const newActive = document.getElementById(`lyric-${activeIdx}`);
            if (newActive) {
                newActive.classList.add('active');
                // เลื่อนให้บรรทัดที่ร้องอยู่เด้งมาตรงกลางจอเสมอ แบบนุ่มๆ
                newActive.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            lastLyricIndex = activeIdx;
        }
    }
});

// ตอนผู้ใช้กำลังลากหลอดเวลา
progressBar.addEventListener('input', () => {
    isDraggingProgress = true;
    if (player.duration) currentTimeEl.innerText = formatTime((progressBar.value / 100) * player.duration);
});

// ปล่อยเมาส์ปุ๊บ กรอเพลงปั๊บ
progressBar.addEventListener('change', () => {
    if (player.duration) player.currentTime = (progressBar.value / 100) * player.duration;
    isDraggingProgress = false;
});

/* =========================================
   🖥️ [App Mode] ระบบขยายเต็มจอ (Fullscreen)
   ========================================= */
function toggleFullScreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => { });
    } else {
        if (document.exitFullscreen) { document.exitFullscreen(); }
    }
}

document.addEventListener('dblclick', (e) => {
    const isInteractive = e.target.closest('button') || e.target.closest('input') || e.target.closest('.search-result-item') || e.target.closest('.queue-item') || e.target.closest('.premium-control-bar') || e.target.closest('.progress-container');
    if (isInteractive) return;
    toggleFullScreen();
});

/* =========================================
   ♾️ [Endless Radio] ระบบเล่นเพลงอัตโนมัติ (Watchdog AI)
   ========================================= */
let isAutoPlayEnabled = false;
let isFetchingAutoPlay = false;

function toggleAutoPlay() {
    isAutoPlayEnabled = !isAutoPlayEnabled;
    const btn = document.getElementById('autoPlayBtn');
    if (isAutoPlayEnabled) {
        btn.classList.add('active-autoplay');
        if (currentIndex === bookingQueue.length - 1) { preloadNextAutoSong(); }
    } else {
        btn.classList.remove('active-autoplay');
    }
}

setInterval(() => {
    if (isAutoPlayEnabled && bookingQueue.length > 0) {
        if (currentIndex === bookingQueue.length - 1 && !isFetchingAutoPlay) { preloadNextAutoSong(); }
    }
}, 2000);

async function preloadNextAutoSong() {
    if (isFetchingAutoPlay) return;
    isFetchingAutoPlay = true;

    const currentSong = bookingQueue[currentIndex];
    if (!currentSong) { isFetchingAutoPlay = false; return; }

    const title = typeof currentSong === 'string' ? currentSong : currentSong.title;

    let query = title;
    if (title.includes('-')) {
        const artist = title.split('-')[0].trim();
        const randomSuffix = ["official", "playlist", "hits", "live"][Math.floor(Math.random() * 4)];
        query = `${artist} ${randomSuffix}`;
    } else {
        query = title + " song";
    }

    try {
        const res = await fetch(`/search?q=${encodeURIComponent(query)}`);
        const songs = await res.json();

        const cleanTitle = (t) => t.toLowerCase().replace(/\[.*?\]|\(.*?\)|official|video|audio|lyrics|mv|hd/g, '').trim();

        const newSongs = songs.filter(s => {
            const sClean = cleanTitle(s.title);
            return !bookingQueue.some(q => {
                const qTitle = typeof q === 'string' ? q : q.title;
                return q.url === s.url || cleanTitle(qTitle) === sClean;
            });
        });

        if (newSongs.length > 0) {
            const randomIndex = Math.floor(Math.random() * Math.min(8, newSongs.length));
            const nextSong = newSongs[randomIndex];
            addSong(nextSong.url, nextSong.title, null);
        }
    } catch (e) {
    } finally {
        setTimeout(() => { isFetchingAutoPlay = false; }, 2000);
    }
}

/* =========================================
   👁️ [Focus Mode] ซ่อนแถบซ้ายเมื่อคลิกพื้นที่ว่าง
   ========================================= */
document.addEventListener('click', (e) => {
    const isInteractive = e.target.closest('button') || e.target.closest('input') || e.target.closest('.search-result-item') || e.target.closest('.queue-item') || e.target.closest('.premium-control-bar') || e.target.closest('.progress-container') || e.target.closest('.sidebar-left') || e.target.closest('.sidebar-right') || e.target.closest('video');
    if (isInteractive) return;
    document.body.classList.toggle('collapse-left');
});

/* =========================================
   🎤 [Lyrics API] ค้นหาและซิงค์เนื้อเพลง
   ========================================= */
let currentLyrics = [];
let lastLyricIndex = -1;

function toggleLyrics() {
    document.body.classList.toggle('lyrics-active');
    const lyricsBtn = document.getElementById('lyricsBtn');
    if (document.body.classList.contains('lyrics-active')) {
        if (lyricsBtn) lyricsBtn.classList.add('active-lyrics');
        fetchLyricsForCurrentSong();
    } else {
        if (lyricsBtn) lyricsBtn.classList.remove('active-lyrics');
    }
}

async function fetchLyricsForCurrentSong() {
    const titleEl = document.getElementById('currentSongTitle').innerText;
    const lyricsContent = document.getElementById('lyricsContent');
    if (titleEl === "เพลย์ลิสต์ที่ดีที่สุด" || titleEl.includes("⏳")) return;

    lyricsContent.innerHTML = `<div class="lyric-line active">กำลังค้นหาเนื้อเพลง...</div>`;
    currentLyrics = [];
    lastLyricIndex = -1;

    let cleanTitle = titleEl.replace(/\[.*?\]|\(.*?\)|official|video|audio|mv|lyrics/gi, '').trim();

    let coreTrackName = cleanTitle;
    if (cleanTitle.includes('-')) {
        const parts = cleanTitle.split('-');
        coreTrackName = parts[parts.length - 1].trim();
    }

    try {
        const res = await fetch(`https://lrclib.net/api/search?q=${encodeURIComponent(cleanTitle)}`);
        const data = await res.json();

        const trackWithLyrics = data.find(t => {
            if (!t.syncedLyrics) return false;

            const apiTrackName = t.trackName.toLowerCase();
            const myTrackName = coreTrackName.toLowerCase();
            const fullTitle = cleanTitle.toLowerCase();

            return apiTrackName.includes(myTrackName) || myTrackName.includes(apiTrackName) || fullTitle.includes(apiTrackName);
        });

        if (trackWithLyrics) {
            parseLyrics(trackWithLyrics.syncedLyrics);
        } else {
            lyricsContent.innerHTML = `<div class="lyric-line" style="filter: blur(0); color: rgba(255,255,255,0.5); font-size: 24px; transform: scale(1);">ยังไม่มีเนื้อเพลง...</div>`;
        }
    } catch (err) {
        lyricsContent.innerHTML = `<div class="lyric-line">เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์เนื้อเพลง</div>`;
    }
}

// ถอดรหัสเวลาจากไฟล์ LRC มาเป็นวินาทีให้วิดีโอเข้าใจ
function parseLyrics(lrcString) {
    const lines = lrcString.split('\n');
    currentLyrics = [];
    const regex = /\[(\d{2}):(\d{2}\.\d{2,3})\](.*)/;

    let html = '';
    lines.forEach((line) => {
        const match = line.match(regex);
        if (match) {
            const mins = parseInt(match[1]);
            const secs = parseFloat(match[2]);
            const text = match[3].trim();
            if (text) {
                const time = mins * 60 + secs;
                // 🔥 3. เปลี่ยนจากวาร์ปตรงๆ เป็นการเรียก smoothSeekTo()
                html += `<div class="lyric-line" id="lyric-${currentLyrics.length}" onclick="smoothSeekTo(${time});">${text}</div>`;
                currentLyrics.push({ time, text });
            }
        }
    });

    document.getElementById('lyricsContent').innerHTML = html || `<div class="lyric-line">อ่านเนื้อเพลงไม่ได้</div>`;
}

// ดักตอนเปลี่ยนเพลง: ถ้าเปิดโหมด L ค้างไว้ ให้ดึงเนื้อเพลงใหม่ทันที
const originalExecutePlay = executePlay;
executePlay = function (index) {
    originalExecutePlay(index);
    if (document.body.classList.contains('lyrics-active')) {
        setTimeout(fetchLyricsForCurrentSong, 1500);
    }
};

/* =========================================
   💬 [Custom Tooltip] แปลง title ธรรมดาให้เป็น Tooltip พรีเมียม
   ========================================= */
// ค้นหาทุกปุ่ม/กล่องที่มีคำใบ้ (title)
document.querySelectorAll('[title]').forEach(el => {
    // ย้ายข้อความไปไว้ในกล่องดีไซน์ใหม่
    el.setAttribute('data-tooltip', el.getAttribute('title'));
    // ลบ title เดิมทิ้ง เบราว์เซอร์จะได้ไม่โชว์กล่องสี่เหลี่ยมแข็งๆ ซ้ำ
    el.removeAttribute('title');
});
/* =========================================
   ⌨️ [Esc Master] กดปุ่ม Esc เพื่อออกจากทุกโหมด
   ========================================= */
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        // 1. ถ้าอยู่ในโหมดเนื้อเพลง -> ปิดเนื้อเพลง
        if (document.body.classList.contains('lyrics-active')) {
            toggleLyrics();
        }

        // 2. ถ้าอยู่ในโหมดโรงหนัง (Theater) -> ปิดโรงหนัง
        if (document.body.classList.contains('theater-mode')) {
            toggleTheater();
        }

        // 3. ถ้าอยู่ในโหมด PiP (จอเล็ก) -> ปิดจอเล็ก
        if (document.pictureInPictureElement) {
            document.exitPictureInPicture();
        }

        // 4. ถ้าอยู่ในโหมดเต็มจอ (Fullscreen) -> ออกจากเต็มจอ
        if (document.fullscreenElement) {
            document.exitFullscreen();
        }

        // 5. ถ้าแถบซ้ายพับอยู่ -> ให้กางออกมา (คืนค่าปกติ)
        if (document.body.classList.contains('collapse-left')) {
            document.body.classList.remove('collapse-left');
        }

        // 6. ถ้ามีกล่อง Suggestion ค้นหาค้างอยู่ -> ให้ซ่อนไป
        const suggestions = document.getElementById('suggestions');
        if (suggestions) {
            suggestions.style.display = 'none';
        }

        resetIdleTimer(); // รีเซ็ตเวลาพักจอด้วย
    }
});

/* ==========================================
   🌊 เอนจิ้นโช้คอัพเสียง (Smooth Volume Lerp)
   ========================================== */
let volAnimationId;

function smoothVolumeChange(targetVol) {
    // ล็อกเพดานไม่ให้เสียงทะลุ 0 (ปิดเสียง) หรือ 1 (ดังสุด)
    targetVol = Math.max(0, Math.min(1, targetVol));

    // ยกเลิกแอนิเมชันเก่าที่อาจจะค้างอยู่ (กันหลอดสั่น)
    cancelAnimationFrame(volAnimationId);

    function animateVol() {
        let currentVol = player.volume;
        // สมการโช้คอัพ: ขยับเสียงปัจจุบันไปหาเป้าหมายทีละ 10% เพื่อความสมูท
        let newVol = currentVol + (targetVol - currentVol) * 0.1;

        if (Math.abs(targetVol - newVol) < 0.005) {
            // ถ้าใกล้ถึงเป้าหมายมากๆ แล้ว ให้ปัดเศษเข้าเส้นชัยไปเลย
            player.volume = targetVol;
            if (document.getElementById('volumeSlider')) {
                document.getElementById('volumeSlider').value = targetVol;
            }
        } else {
            // ถ้ายังไม่ถึงเป้าหมาย ให้ค่อยๆ รูดหลอดขยับต่อไป
            player.volume = newVol;
            if (document.getElementById('volumeSlider')) {
                document.getElementById('volumeSlider').value = newVol;
            }
            // สั่งรันเฟรมต่อไป (ทำงานที่ 60FPS)
            volAnimationId = requestAnimationFrame(animateVol);
        }
    }
    animateVol(); // สตาร์ทเครื่องยนต์
}
