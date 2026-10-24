let bookingQueue = [];
let currentIndex = -1;
let dragStartIndex = -1;
const player = document.getElementById('player');
const videoCard = document.querySelector('.video-card');
const dynamicBg = document.getElementById('dynamic-bg');
let suggestTimeout;

document.addEventListener('contextmenu', event => event.preventDefault());

player.addEventListener('loadedmetadata', () => {
    if (player.videoWidth && player.videoHeight) {
        const ratio = player.videoWidth / player.videoHeight;
        player.style.aspectRatio = `${ratio}`;
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

let currentRGB = [0, 113, 227];
let targetRGB = [0, 113, 227];
let lastRenderedRGB = "";

function updateGlow() {
    const rgbStr = getDynamicColor();
    if (!rgbStr) return;

    const newColors = rgbStr.split(',').map(Number);

    const diff = Math.abs(newColors[0] - targetRGB[0]) +
        Math.abs(newColors[1] - targetRGB[1]) +
        Math.abs(newColors[2] - targetRGB[2]);

    if (diff > 25) {
        targetRGB = newColors;
    }

    currentRGB[0] += (targetRGB[0] - currentRGB[0]) * 0.2;
    currentRGB[1] += (targetRGB[1] - currentRGB[1]) * 0.2;
    currentRGB[2] += (targetRGB[2] - currentRGB[2]) * 0.2;

    const r = Math.round(currentRGB[0]);
    const g = Math.round(currentRGB[1]);
    const b = Math.round(currentRGB[2]);
    const smoothRgbStr = `${r}, ${g}, ${b}`;

    if (smoothRgbStr === lastRenderedRGB) return;
    lastRenderedRGB = smoothRgbStr;

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

setInterval(updateGlow, 100);

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

setInterval(() => {
    const rgbStr = getDynamicColor() || '0, 113, 227';
    const currentTitle = document.getElementById('currentSongTitle').innerText;
    let nextTitle = document.getElementById('upNextDisplay').innerText.replace('ถัดไป:', '').trim();
    if (nextTitle === '-' || nextTitle === '') nextTitle = '-';

    let thumbUrl = "";
    const song = bookingQueue[currentIndex];

    if (song) {

        if (song.url && song.url.includes('v=')) {
            const match = song.url.match(/v=([^&]+)/);
            if (match) {
                thumbUrl = `https://i.ytimg.com/vi/${match[1]}/hqdefault.jpg`;
                song.thumb = thumbUrl;
            }
        }

        else if (!song.thumb) {
            song.thumb = "searching";
            const query = song.title || song;
            fetch(`/search?q=${encodeURIComponent(query)}`)
                .then(r => r.json())
                .then(data => {
                    if (data && data.length > 0 && data[0].thumbnail) {
                        song.thumb = data[0].thumbnail;
                    } else {
                        song.thumb = "notfound";
                    }
                }).catch(() => { });
        }

        if (!thumbUrl && song.thumb && song.thumb !== "searching" && song.thumb !== "notfound") {
            thumbUrl = song.thumb;
        }
    }

    const time = player.currentTime || 0;
    const duration = player.duration || 0;

    const currentVolSlider = document.getElementById('volumeSlider') ? document.getElementById('volumeSlider').value : 1;

    fetch(`/state/update?rgb=${encodeURIComponent(rgbStr)}&current=${encodeURIComponent(currentTitle)}&next_song=${encodeURIComponent(nextTitle)}&playing=${!player.paused}&thumb=${encodeURIComponent(thumbUrl)}&time=${time}&duration=${duration}&vol=${currentVolSlider}`)
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

    }
}, 1000);

document.addEventListener('keydown', (e) => {

    if (e.target.tagName === 'INPUT') return;

    if (e.code === 'Space') { e.preventDefault(); togglePlay(); }
    else if (e.code === 'ArrowRight') { e.preventDefault(); playNext(); }
    else if (e.code === 'ArrowLeft') { e.preventDefault(); playPrevious(); }

    else if (e.code === 'ArrowUp') {
        e.preventDefault();
        const slider = document.getElementById('volumeSlider');
        slider.value = Math.min(1, parseFloat(slider.value) + 0.1);
        changeVolume();
    }
    else if (e.code === 'ArrowDown') {
        e.preventDefault();
        const slider = document.getElementById('volumeSlider');
        slider.value = Math.max(0, parseFloat(slider.value) - 0.1);
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

window.addEventListener('DOMContentLoaded', () => {
    const savedVol = localStorage.getItem('karaoke_volume');
    if (savedVol !== null) {
        player.volume = parseFloat(savedVol);
        document.getElementById('volumeSlider').value = savedVol;
        updateVolIcon();
    }
});

function changeVolume() {
    player.volume = document.getElementById('volumeSlider').value;
    localStorage.setItem('karaoke_volume', player.volume);
    updateVolIcon();
}

let lastVol = 1;
function toggleMute() {
    if (player.volume > 0) {
        lastVol = player.volume;
        player.volume = 0;
        document.getElementById('volumeSlider').value = 0;
    } else {
        player.volume = lastVol > 0 ? lastVol : 0.5;
        document.getElementById('volumeSlider').value = player.volume;
    }
    localStorage.setItem('karaoke_volume', player.volume);
    updateVolIcon();
}

function updateVolIcon() {
    const volIcon = document.getElementById('volIcon');
    if (player.volume === 0) {
        volIcon.innerHTML = `<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line>`;
    } else {
        volIcon.innerHTML = `<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>`;
    }
}

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
        document.getElementById('currentSongTitle').innerText = " รอโหลดไฟล์แป๊บนึงน้า...";
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
        player.style.aspectRatio = '';
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
                <div class="drag-handle"></div>
                <div style="color:#ffffff; font-weight:600; min-width:20px; display:flex; justify-content:center;">${indexDisplay}</div>
                <div class="queue-name">${formatTitle(displayTitle)}</div>
                <button class="btn-remove" onclick="removeSong(event, ${index})" title="ลบออกจากคิว"></button>
            </div>`;
    });
    document.getElementById('readyQueue').innerHTML = html || '<p style="color:#86868b; text-align:center; font-weight:400; font-size:13px;">ยังไม่มีเพลงในคิวจ้า</p>';
    updateUpNext();
}

function playNext() {
    if (currentIndex + 1 < bookingQueue.length) {
        playAtIndex(currentIndex + 1);
    } else if (isAutoPlayEnabled) {
        preloadNextAutoSong();
    }
}

function playPrevious() {
    if (player.currentTime > 3) {

        fadeAndRestartCurrent();
    } else if (currentIndex - 1 >= 0) {
        playAtIndex(currentIndex - 1);
    }
}

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
            animateProgressBack();

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

async function playAtIndex(index) {
    if (index < 0 || index >= bookingQueue.length) return;

    if (player.isFading) return;

    if (!player.paused && player.volume > 0) {
        player.isFading = true;
        let vol = player.volume;

        const fadeOut = setInterval(() => {
            vol -= 0.05;
            if (vol <= 0) {
                player.volume = 0;
                clearInterval(fadeOut);
                player.isFading = false;
                executePlay(index);
            } else {
                player.volume = vol;
            }
        }, 30);
    } else {
        executePlay(index);
    }
}

function executePlay(index) {
    animateProgressBack();

    currentIndex = index;
    const song = bookingQueue[index];
    const isStr = typeof song === 'string';
    const displayTitle = isStr ? song : song.title;
    const filename = isStr ? song : song.fileName;

    if (song && !song.thumb) {
        if (song.url) {

            const match = song.url.match(/v=([^&]+)/);
            if (match) song.thumb = `https://i.ytimg.com/vi/${match[1]}/hqdefault.jpg`;
        } else {

            fetch(`/search?q=${encodeURIComponent(displayTitle)}`)
                .then(res => res.json())
                .then(data => {
                    if (data && data.length > 0 && data[0].thumbnail) {
                        song.thumb = data[0].thumbnail;
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
        document.getElementById('currentSongTitle').innerText = " รอโหลดไฟล์แป๊บนึงน้า...";
    }
    renderQueue();
}

async function playAtIndex(index) {
    if (index < 0 || index >= bookingQueue.length) return;

    if (player.isFading) return;

    if (!player.paused && player.volume > 0) {
        player.isFading = true;
        let vol = player.volume;

        const fadeOut = setInterval(() => {
            vol = Math.max(0, vol - 0.05);
            player.volume = vol;
            if (vol <= 0) {
                clearInterval(fadeOut);
                player.isFading = false;
                executePlay(index);
            }
        }, 30);
    } else {
        executePlay(index);
    }
}

function animateProgressBack() {
    isDraggingProgress = true;
    let currentVal = parseFloat(progressBar.value);

    if (currentVal <= 0) {
        isDraggingProgress = false;
        return;
    }

    const step = currentVal / 20;
    const slideBack = setInterval(() => {
        currentVal -= step;
        if (currentVal <= 0) {
            progressBar.value = 0;
            currentTimeEl.innerText = "0:00";
            clearInterval(slideBack);
            isDraggingProgress = false;
        } else {
            progressBar.value = currentVal;
        }
    }, 15);
}

function executePlay(index) {

    animateProgressBack();

    currentIndex = index;
    const song = bookingQueue[index];
    const isStr = typeof song === 'string';
    const displayTitle = isStr ? song : song.title;
    const filename = isStr ? song : song.fileName;

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
        document.getElementById('currentSongTitle').innerText = " รอโหลดไฟล์แป๊บนึงน้า...";
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

setInterval(() => {
    const currentTitle = document.getElementById('currentSongTitle').innerText;

    if (currentTitle !== "เพลย์ลิสต์ที่ดีที่สุด" && currentTitle !== " รอโหลดไฟล์แป๊บนึงน้า...") {
        document.title = currentTitle;
        setupMediaSession(currentTitle);
    } else {
        document.title = "Music Studio - Space";
    }
}, 1000);

const favCanvas = document.createElement('canvas');
favCanvas.width = 32;
favCanvas.height = 32;
const favCtx = favCanvas.getContext('2d');

let favLink = document.querySelector("link[rel~='icon']");
if (!favLink) {
    favLink = document.createElement('link');
    favLink.rel = 'icon';
    document.head.appendChild(favLink);
}

function updateFavicon() {

    favCtx.clearRect(0, 0, 32, 32);

    const rgbStr = document.documentElement.style.getPropertyValue('--theme-rgb') || '255, 255, 255';
    favCtx.fillStyle = `rgb(${rgbStr})`;

    if (player && !player.paused && player.src) {

        const h1 = 12 + Math.random() * 20;
        const h2 = 12 + Math.random() * 20;
        const h3 = 12 + Math.random() * 20;

        favCtx.beginPath();
        favCtx.roundRect(4, 32 - h1, 6, h1, 2);
        favCtx.roundRect(13, 32 - h2, 6, h2, 2);
        favCtx.roundRect(22, 32 - h3, 6, h3, 2);
        favCtx.fill();
    } else {

        favCtx.beginPath();
        favCtx.roundRect(4, 24, 6, 8, 2);
        favCtx.roundRect(13, 16, 6, 16, 2);
        favCtx.roundRect(22, 20, 6, 12, 2);
        favCtx.fill();
    }

    favLink.href = favCanvas.toDataURL('image/png');
}

setInterval(updateFavicon, 250);

const progressBar = document.getElementById('progressBar');
const currentTimeEl = document.getElementById('currentTime');
const durationTimeEl = document.getElementById('durationTime');
let isDraggingProgress = false;

let isSliderAnimating = false;

function smoothSeekTo(targetTime) {
    if (!player.duration) return;
    const startPercent = parseFloat(progressBar.value);
    const endPercent = (targetTime / player.duration) * 100;
    const duration = 400;
    const startTime = performance.now();

    isSliderAnimating = true;
    player.currentTime = targetTime;

    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const currentPercent = startPercent + (endPercent - startPercent) * easeOutQuart;

        progressBar.value = currentPercent;
        progressBar.dispatchEvent(new Event('input'));

        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            isSliderAnimating = false;
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

player.addEventListener('timeupdate', () => {

    if (!isDraggingProgress && !isSliderAnimating && player.duration) {
        progressBar.value = (player.currentTime / player.duration) * 100;
        currentTimeEl.innerText = formatTime(player.currentTime);
        durationTimeEl.innerText = formatTime(player.duration);
    }

    if (document.body.classList.contains('lyrics-active') && currentLyrics.length > 0) {
        const currentTime = player.currentTime;
        let activeIdx = -1;

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

                newActive.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            lastLyricIndex = activeIdx;
        }
    }
});

progressBar.addEventListener('input', () => {
    isDraggingProgress = true;
    if (player.duration) currentTimeEl.innerText = formatTime((progressBar.value / 100) * player.duration);
});

progressBar.addEventListener('change', () => {
    if (player.duration) player.currentTime = (progressBar.value / 100) * player.duration;
    isDraggingProgress = false;
});

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

document.addEventListener('click', (e) => {
    const isInteractive = e.target.closest('button') || e.target.closest('input') || e.target.closest('.search-result-item') || e.target.closest('.queue-item') || e.target.closest('.premium-control-bar') || e.target.closest('.progress-container') || e.target.closest('.sidebar-left') || e.target.closest('.sidebar-right') || e.target.closest('video');
    if (isInteractive) return;
    document.body.classList.toggle('collapse-left');
});

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
    if (titleEl === "เพลย์ลิสต์ที่ดีที่สุด" || titleEl.includes("")) return;

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

                html += `<div class="lyric-line" id="lyric-${currentLyrics.length}" onclick="smoothSeekTo(${time});">${text}</div>`;
                currentLyrics.push({ time, text });
            }
        }
    });

    document.getElementById('lyricsContent').innerHTML = html || `<div class="lyric-line">อ่านเนื้อเพลงไม่ได้</div>`;
}

const originalExecutePlay = executePlay;
executePlay = function (index) {
    originalExecutePlay(index);
    if (document.body.classList.contains('lyrics-active')) {
        setTimeout(fetchLyricsForCurrentSong, 1500);
    }
};

document.querySelectorAll('[title]').forEach(el => {

    el.setAttribute('data-tooltip', el.getAttribute('title'));

    el.removeAttribute('title');
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {

        if (document.body.classList.contains('lyrics-active')) {
            toggleLyrics();
        }

        if (document.body.classList.contains('theater-mode')) {
            toggleTheater();
        }

        if (document.pictureInPictureElement) {
            document.exitPictureInPicture();
        }

        if (document.fullscreenElement) {
            document.exitFullscreen();
        }

        if (document.body.classList.contains('collapse-left')) {
            document.body.classList.remove('collapse-left');
        }

        const suggestions = document.getElementById('suggestions');
        if (suggestions) {
            suggestions.style.display = 'none';
        }

        resetIdleTimer();
    }
});

let volAnimationId;

function smoothVolumeChange(targetVol) {

    targetVol = Math.max(0, Math.min(1, targetVol));

    cancelAnimationFrame(volAnimationId);

    function animateVol() {
        let currentVol = player.volume;

        let newVol = currentVol + (targetVol - currentVol) * 0.1;

        if (Math.abs(targetVol - newVol) < 0.005) {

            player.volume = targetVol;
            if (document.getElementById('volumeSlider')) {
                document.getElementById('volumeSlider').value = targetVol;
            }
        } else {

            player.volume = newVol;
            if (document.getElementById('volumeSlider')) {
                document.getElementById('volumeSlider').value = newVol;
            }

            volAnimationId = requestAnimationFrame(animateVol);
        }
    }
    animateVol();
}
