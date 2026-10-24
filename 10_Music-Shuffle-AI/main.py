import sys
import os
import json
import asyncio
import subprocess
import random
import urllib.request
import urllib.parse
import re
import time


os.environ.setdefault("QT_LOGGING_RULES",
    "*.debug=false;qt.qpa.*=false;qt.multimedia.*=false")
os.environ.setdefault("AV_LOG_FORCE_NOCOLOR", "1")
os.environ.setdefault("PYTHONWARNINGS", "ignore")


from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QListWidget, 
                             QSlider, QLineEdit, QListWidgetItem,
                             QStackedLayout, QFrame, QSizePolicy, QGraphicsOpacityEffect,
                             QMenu, QInputDialog, QMessageBox, QDialog,
                             QStyledItemDelegate, QStyle, QAbstractItemView, QWidgetAction,
                             QTextEdit, QScrollArea)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl, QThread, pyqtSignal, pyqtSlot, QByteArray, QTimer, QPropertyAnimation, QEasingCurve, QVariantAnimation, QSize, QRect, QRectF, pyqtProperty, QParallelAnimationGroup
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QImage, QPainterPath, QPalette
from PyQt6.QtSvg import QSvgRenderer

try:
    import syncedlyrics
except ImportError:
    syncedlyrics = None

try:
    import faster_whisper
except ImportError:
    faster_whisper = None

class LyricLabel(QWidget):
    lyric_clicked = pyqtSignal(int)

    def __init__(self, text, time_ms):
        super().__init__()
        self._text = text
        self.time_ms = time_ms
        self.setMinimumHeight(70) 
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self._scale_factor = 0.69         
        self._opacity = 100.0


        self._font = self.font()
        self._font.setPointSizeF(26.0)
        self._font.setBold(True)
        self.anim_group = None

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lyric_clicked.emit(self.time_ms)
        super().mouseReleaseEvent(event)

    @pyqtProperty(float)
    def scale_factor(self):
        return self._scale_factor

    @scale_factor.setter
    def scale_factor(self, value):
        self._scale_factor = value
        self.update()

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        rect = self.rect()


        painter.translate(rect.center())
        painter.scale(self._scale_factor, self._scale_factor)
        painter.translate(-rect.center())

        painter.setFont(self._font)
        painter.setPen(QColor(255, 255, 255, int(self._opacity)))


        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, self._text)

class LyricsFetcherThread(QThread):
    lyrics_found = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        if not syncedlyrics:
            self.error_occurred.emit("โปรดรีสตาร์ทแอปเพื่อโหลดไลบรารี syncedlyrics")
            return
        try:
            lrc = syncedlyrics.search(self.query)
            if lrc:
                self.lyrics_found.emit(lrc)
            else:
                self.error_occurred.emit("ไม่พบเนื้อเพลงในระบบออนไลน์")
        except Exception as e:
            self.error_occurred.emit(str(e))

class WhisperTranscriberThread(QThread):
    transcription_done = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    progress_update = pyqtSignal(str)
    lyric_line_yielded = pyqtSignal(int, str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        if not faster_whisper:
            self.error_occurred.emit("โปรดรีสตาร์ทแอปเพื่อโหลดไลบรารี faster-whisper")
            return
        try:
            self.progress_update.emit("กำลังเตรียมโมเดล AI 'Medium' (โหลดครั้งแรกอาจใช้เวลาสักครู่ โหลดเสร็จแล้วจะเร็วมาก)...")

            import os
            model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_models")
            os.makedirs(model_dir, exist_ok=True)


            model = faster_whisper.WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", download_root=model_dir)

            self.progress_update.emit("กำลังใช้ AI วิเคราะห์เสียงร้อง (โหมดความเร็วสูง)...\n(เนื้อเพลงจะทยอยปรากฏขึ้นมา)")
            kwargs = dict(
                beam_size=5,
                word_timestamps=True,
                condition_on_previous_text=False,
                initial_prompt="เนื้อเพลงภาษาไทย",
                vad_filter=True, 
                vad_parameters=dict(min_silence_duration_ms=1000, speech_pad_ms=400),

                compression_ratio_threshold=1.8,                              
                log_prob_threshold=-0.5,                                           
                no_speech_threshold=0.4                                                      
            )

            segments, info = model.transcribe(self.file_path, **kwargs)


            if info.language == "zh":
                segments, info = model.transcribe(self.file_path, language="th", **kwargs)

            lrc_lines = []
            for segment in segments:
                text = segment.text.strip()
                if not text or "作曲" in text or "作词" in text or "李宗盛" in text:
                    continue                                   


                actual_start = segment.words[0].start if getattr(segment, 'words', None) else segment.start

                m = int(actual_start // 60)
                s = int(actual_start % 60)
                ms = int((actual_start % 1) * 100)

                time_ms_int = int(actual_start * 1000)
                self.lyric_line_yielded.emit(time_ms_int, text)

                lrc_lines.append(f"[{m:02d}:{s:02d}.{ms:02d}] {text}")

            self.transcription_done.emit("\n".join(lrc_lines))
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(str(e))


SVG_DEFS = {
    "play": '<svg viewBox="0 0 24 24"><polygon points="7,4 20,12 7,20" fill="currentColor"/></svg>',
    "pause": '<svg viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16" rx="1.5" fill="currentColor"/><rect x="14" y="4" width="4" height="16" rx="1.5" fill="currentColor"/></svg>',
    "prev": '<svg viewBox="0 0 24 24"><polygon points="19,19 9,12 19,5" fill="currentColor"/><line x1="5" y1="5" x2="5" y2="19" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>',
    "next": '<svg viewBox="0 0 24 24"><polygon points="5,5 15,12 5,19" fill="currentColor"/><line x1="19" y1="5" x2="19" y2="19" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>',
    "shuffle": '<svg viewBox="0 0 24 24"><path d="M16 3h5v5M4 20l7-7m9-10l-5 5M4 4l5 5m6 6l5 5m0-5v5h-5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "repeat": '<svg viewBox="0 0 24 24"><path d="m17 2 4 4-4 4M3 11v-1a4 4 0 0 1 4-4h14M7 22l-4-4 4-4M21 13v1a4 4 0 0 1-4 4H3" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "volume": '<svg viewBox="0 0 24 24"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" fill="currentColor"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
    "volume_mute": '<svg viewBox="0 0 24 24"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" fill="currentColor"/><line x1="22" y1="9" x2="16" y2="15" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><line x1="16" y1="9" x2="22" y2="15" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
    "search": '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2.2"/><line x1="21" y1="21" x2="16" y2="16" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
    "disc": '''<svg viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="56" fill="#13141b" stroke="#252735" stroke-width="2.5"/>
        <circle cx="60" cy="60" r="46" fill="none" stroke="#1d1e28" stroke-width="1.5"/>
        <circle cx="60" cy="60" r="36" fill="none" stroke="#252735" stroke-width="1.5"/>
        <circle cx="60" cy="60" r="23" fill="#8b5cf6"/>
        <circle cx="60" cy="60" r="8" fill="#0d0e12"/>
    </svg>''',
    "heart": '<svg viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "heart_filled": '<svg viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "plus": '<svg viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>',
    "trash": '<svg viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "playlist_icon": '<svg viewBox="0 0 24 24"><line x1="8" y1="6" x2="21" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="8" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="8" y1="18" x2="21" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M3 6l1 1 2-3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="3.5" cy="12" r="0.5" fill="currentColor"/><circle cx="3.5" cy="18" r="0.5" fill="currentColor"/></svg>',
    "autoplay": '<svg viewBox="0 0 24 24"><path d="M9.98 2.6l1.32 4.14 4.14 1.32-4.14 1.32-1.32 4.14-1.32-4.14-4.14-1.32 4.14-1.32 1.32-4.14zm9.36 10.66l.87 2.76 2.76.87-2.76.87-.87 2.76-.87-2.76-2.76-.87 2.76-.87.87-2.76zm-3.14-5.33l.87 2.76 2.76.87-2.76.87-.87 2.76-.87-2.76-2.76-.87 2.76-.87.87-2.76z" fill="currentColor"/></svg>'
}

def render_svg_icon(name, color="#ffffff", size=24):
    raw = SVG_DEFS[name].replace("currentColor", color)
    renderer = QSvgRenderer(QByteArray(raw.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("transparent"))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

def create_styled_action(menu, icon_name, icon_color, text, callback):
    action = QWidgetAction(menu)
    btn = QPushButton("   " + text)
    btn.setIcon(render_svg_icon(icon_name, icon_color, 16))
    btn.setIconSize(QSize(16, 16))
    btn.setStyleSheet("""
        QPushButton {
            background: transparent;
            color: #d4d4d8;
            border: none;
            text-align: left;
            padding: 8px 12px;
            border-radius: 6px;
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            margin: 2px 6px;
        }
        QPushButton:hover {
            background-color: #8b5cf6;
            color: #ffffff;
        }
    """)
    action.setDefaultWidget(btn)
    if callback:
        btn.clicked.connect(callback)
    btn.clicked.connect(menu.close)
    menu.addAction(action)
    return action

def render_svg_pixmap(name, color="#ffffff", size=96):
    raw = SVG_DEFS[name].replace("currentColor", color)
    renderer = QSvgRenderer(QByteArray(raw.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("transparent"))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


class SearchThread(QThread):
    results_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        try:
            command = ["yt-dlp", "--extractor-args", "youtube:player_client=ios", f"ytsearch10:{self.query}", "--dump-json", "--flat-playlist", "--quiet"]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                self.error_occurred.emit(stderr)
                return

            results = []
            for line in stdout.strip().split('\n'):
                if not line: continue
                entry = json.loads(line)

                thumbnail = None
                if 'thumbnails' in entry and entry['thumbnails']:

                    valid_thumbs = [t for t in entry['thumbnails'] if t.get('url')]
                    if valid_thumbs:
                        thumbnail = valid_thumbs[-1]['url']
                elif 'thumbnail' in entry:
                    thumbnail = entry['thumbnail']

                results.append({
                    "title": entry.get('title'),
                    "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                    "id": entry.get('id'),
                    "thumbnail": thumbnail
                })
            self.results_ready.emit(results)
        except Exception as e:
            self.error_occurred.emit(str(e))


class YouTubeCoverArtLoaderThread(QThread):
    cover_loaded = pyqtSignal(str, bytes)

    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items                                                                

    def run(self):
        for item in self.items:
            thumb_url = item.get('thumbnail')
            video_url = item.get('url')
            if not thumb_url or not video_url:
                continue
            try:
                req = urllib.request.Request(thumb_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = response.read()
                if data:
                    self.cover_loaded.emit(video_url, data)
            except Exception:
                pass


class DownloadThread(QThread):
    download_completed = pyqtSignal(str, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, url, title):
        super().__init__()
        self.url = url
        self.title = title

    def run(self):
        try:
            import re
            safe_title = re.sub(r'[\\/*?:"<>|]', "", self.title).strip().replace(' ', '_')
            if not os.path.exists("music"):
                os.makedirs("music")

            filepath = f"music/{safe_title}.m4a"

            if not os.path.exists(filepath):
                import subprocess
                command = [
                    "yt-dlp",
                    "-f", "bestaudio[ext=m4a]/bestaudio",
                    "--extract-audio",
                    "--audio-format", "m4a",
                    "--embed-thumbnail",
                    "--embed-metadata",
                    "--no-playlist",
                    "-o", filepath,
                    self.url
                ]
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()

                if process.returncode != 0:
                    raise Exception(f"yt-dlp failed: {stderr.strip()}")
                if not os.path.exists(filepath):
                    raise Exception("yt-dlp succeeded but file was not created.")

            self.download_completed.emit(self.title, filepath)
        except Exception as e:
            self.error_occurred.emit(str(e))

def get_rounded_pixmap_from_data(image_data, size=240, radius=12, crop=True):
    try:
        image = QImage.fromData(image_data)
        if image.isNull():
            return None

        if crop:
            scaled = image.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            crop_x = (scaled.width() - size) // 2
            crop_y = (scaled.height() - size) // 2
            cropped = scaled.copy(crop_x, crop_y, size, size)
        else:
            scaled = image.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            cropped = scaled

        target = QPixmap(cropped.size())
        target.fill(Qt.GlobalColor.transparent)

        painter = QPainter(target)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        path = QPainterPath()
        path.addRoundedRect(0, 0, cropped.width(), cropped.height(), radius, radius)
        painter.setClipPath(path)
        painter.drawImage(0, 0, cropped)
        painter.end()
        return target
    except Exception as e:
        print(f"Error in get_rounded_pixmap_from_data: {e}")
        return None

def get_dominant_color_from_data(image_data):
    from PyQt6.QtGui import QImage, QColor
    from PyQt6.QtCore import Qt
    img = QImage()
    img.loadFromData(image_data)
    if img.isNull():
        return QColor(24, 25, 34)


    small = img.scaled(1, 1, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
    avg_color = small.pixelColor(0, 0)


    h, s, v, a = avg_color.getHsv()
    s = min(255, int(s * 1.3))
    v = min(255, max(100, int(v * 0.9)))

    avg_color.setHsv(h, s, v, a)
    return avg_color

def extract_cover_art(filepath):
    try:
        import mutagen
        audio = mutagen.File(filepath)
        if audio is None:
            return None
        tags = audio.tags
        if tags is None:
            return None

        if hasattr(audio.tags, 'keys'):
            for key in audio.tags.keys():
                if key.startswith('APIC'):
                    return audio.tags[key].data

        if 'covr' in tags:
            covr = tags['covr']
            if covr:
                return bytes(covr[0])

        if hasattr(audio, 'pictures') and audio.pictures:
            return audio.pictures[0].data
        if hasattr(audio, 'metadata_blocks'):
            from mutagen.flac import Picture
            for block in audio.metadata_blocks:
                if isinstance(block, Picture):
                    return block.data
    except Exception:
        pass
    return None

class CoverArtFetcherThread(QThread):
    cover_fetched = pyqtSignal(str, bytes)

    def __init__(self, filepath, title):
        super().__init__()
        self.filepath = filepath
        self.title = title
        self.is_cancelled = False
        self._process = None

    def cancel(self):
        self.is_cancelled = True
        if self._process:
            try:
                self._process.terminate()
            except:
                pass

    def run(self):
        try:
            clean_title = self.title
            for term in ["official", "music", "video", "lyric", "audio", "mv", r"\[.*?\]", r"\(.*?\)"]:
                clean_title = re.sub(rf'(?i)\b{term}\b', '', clean_title).strip()
            clean_title = re.sub(r'[^\w\s]', ' ', clean_title)
            clean_title = ' '.join(clean_title.split())

            if not clean_title:
                clean_title = self.title

            query = urllib.parse.quote(clean_title)
            url = f"https://itunes.apple.com/search?term={query}&entity=song&limit=1"

            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read())

            artwork_url = None
            if data['resultCount'] > 0:
                artwork_url = data['results'][0].get('artworkUrl100', '')
                if artwork_url:
                    artwork_url = artwork_url.replace('100x100bb', '600x600bb')

            if self.is_cancelled: return


            if not artwork_url:
                yt_query = urllib.parse.quote(self.title)
                yt_url = f"https://www.youtube.com/results?search_query={yt_query}"
                yt_req = urllib.request.Request(yt_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(yt_req, timeout=5) as yt_resp:
                    html = yt_resp.read().decode('utf-8')

                match = re.search(r'"videoId":"([^"]+)"', html)
                if match:
                    artwork_url = f"https://i.ytimg.com/vi/{match.group(1)}/maxresdefault.jpg"

            if self.is_cancelled: return

            if artwork_url:
                req_img = urllib.request.Request(artwork_url, headers={'User-Agent': 'Mozilla/5.0'})
                try:
                    with urllib.request.urlopen(req_img, timeout=5) as response_img:
                        image_data = response_img.read()
                        self.cover_fetched.emit(self.filepath, image_data)
                except urllib.error.HTTPError:
                    if 'maxresdefault' in artwork_url:
                        artwork_url = artwork_url.replace('maxresdefault', 'hqdefault')
                        req_img = urllib.request.Request(artwork_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req_img, timeout=5) as response_img:
                            image_data = response_img.read()
                            self.cover_fetched.emit(self.filepath, image_data)
        except Exception as e:
            print("Cover Fetch Error:", e)

class FadeLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap_a = None
        self._pixmap_b = None
        self._fade_progress = 1.0

        self.anim = QVariantAnimation(self)
        self.anim.valueChanged.connect(self._update_progress)
        self.anim.finished.connect(self._on_finished)
        self.anim.setDuration(400)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def setPixmapWithFade(self, pixmap):
        if self._pixmap_b is None:
            self._pixmap_b = pixmap
            self.setPixmap(pixmap)
            return

        if self.anim.state() == QVariantAnimation.State.Running:
            self.anim.stop()
            self._pixmap_a = self._pixmap_b
        else:
            self._pixmap_a = self.pixmap()

        self._pixmap_b = pixmap
        self._fade_progress = 0.0

        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

    def _update_progress(self, value):
        self._fade_progress = value
        self.update()

    def _on_finished(self):
        self.setPixmap(self._pixmap_b)
        self._pixmap_a = None

    def paintEvent(self, event):
        if self._fade_progress == 1.0 or self._pixmap_a is None:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        def draw_pixmap(px, opacity):
            if px and not px.isNull():
                painter.setOpacity(opacity)
                self.style().drawItemPixmap(painter, self.rect(), int(self.alignment()), px)

        draw_pixmap(self._pixmap_a, 1.0 - self._fade_progress)
        draw_pixmap(self._pixmap_b, self._fade_progress)

class FadeTextLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.effect = QGraphicsOpacityEffect(self)
        self.effect.setOpacity(1.0)
        self.setGraphicsEffect(self.effect)
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(400)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._next_text = ""
        self._full_text = text


        self.has_marquee_token = False
        self.next_marquee_label = None

        self._scroll_x = 0.0
        self._scroll_state = 0                            
        self._scroll_wait_ticks = 0
        from PyQt6.QtCore import QTimer
        self.marquee_timer = QTimer(self)
        self.marquee_timer.timeout.connect(self._on_marquee_tick)
        self.marquee_timer.start(16)                        

    def setNextMarqueeLabel(self, label, is_starter=False):
        self.next_marquee_label = label
        if is_starter:
            self.has_marquee_token = True

    def receive_token(self):
        self.has_marquee_token = True
        self._scroll_state = 0
        self._scroll_wait_ticks = 0

    def _pass_token(self):
        self.has_marquee_token = False
        if self.next_marquee_label:
            self.next_marquee_label.receive_token()

    def setText(self, text):
        self._full_text = text
        super().setText(text)                                
        self._reset_marquee()

    def setTextWithFade(self, text):
        if self._full_text == text:
            return
        if self._full_text == "":
            self.setText(text)
            self.effect.setOpacity(1.0)
            return

        self._next_text = text
        self.anim.setEndValue(0.0)
        if self.anim.receivers(self.anim.finished) > 0:
            self.anim.finished.disconnect()
        self.anim.finished.connect(self._on_fade_out)
        self.anim.start()

    def _on_fade_out(self):
        self.setText(self._next_text)
        self.anim.setEndValue(1.0)
        if self.anim.receivers(self.anim.finished) > 0:
            self.anim.finished.disconnect()
        self.anim.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reset_marquee()

    def _reset_marquee(self):
        self._scroll_x = 0.0
        self._scroll_state = 0
        self._scroll_wait_ticks = 0
        self.update()

    def _on_marquee_tick(self):
        if not self._full_text or self.wordWrap() or self.width() <= 0:
            return

        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self._full_text)

        if text_width <= self.width():
            if self._scroll_x != 0:
                self._reset_marquee()
            if self.has_marquee_token:
                self._pass_token()
            return

        if not self.has_marquee_token:
            if self._scroll_x != 0:
                self._scroll_x = 0.0
                self.update()
            return

        gap = 60                      


        if self._scroll_state == 0:
            self._scroll_wait_ticks += 1
            if self._scroll_wait_ticks > 180:                            
                self._scroll_state = 1
        elif self._scroll_state == 1:
            self._scroll_x -= 0.6
            if self._scroll_x <= -(text_width + gap):

                self._scroll_x = 0.0
                self._scroll_state = 0
                self._scroll_wait_ticks = 0
                self.update()
                self._pass_token()
            else:
                self.update()

    def paintEvent(self, event):
        if not self._full_text:
            return

        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self._full_text)


        if self.wordWrap() or text_width <= self.width() or self.width() <= 0:
            super().paintEvent(event)
            return


        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setClipRect(self.rect())
        painter.setPen(self.palette().color(QPalette.ColorRole.WindowText))

        y = fm.ascent() + (self.height() - fm.height()) // 2

        gap = 60                      

        from PyQt6.QtCore import QPointF
        painter.drawText(QPointF(self._scroll_x, float(y)), self._full_text)
        painter.drawText(QPointF(self._scroll_x + text_width + gap, float(y)), self._full_text)

class ClickableSlider(QSlider):
    seek_committed = pyqtSignal(int)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            val = self.minimum() + ((self.maximum() - self.minimum()) * event.pos().x()) / self.width()
            self.setValue(int(val))
            self.seek_committed.emit(int(val))

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.seek_committed.emit(self.value())


class LocalCoverArtLoaderThread(QThread):
    cover_loaded = pyqtSignal(str, bytes)

    def __init__(self, filepaths, parent=None):
        super().__init__(parent)
        self.filepaths = filepaths

    def run(self):
        import mutagen
        for fp in self.filepaths:
            try:
                audio = mutagen.File(fp)
                if audio is None:
                    continue
                data = None

                tags = audio.tags
                if tags is not None:

                    if hasattr(audio, 'tags') and hasattr(audio.tags, 'getall'):
                        for key in audio.tags.keys():
                            if key.startswith('APIC'):
                                data = audio.tags[key].data
                                break

                    if data is None and 'covr' in tags:
                        covr = tags['covr']
                        if covr:
                            data = bytes(covr[0])

                    if data is None and hasattr(audio, 'pictures') and audio.pictures:
                        data = audio.pictures[0].data

                    if data is None and hasattr(audio, 'metadata_blocks'):
                        from mutagen.flac import Picture
                        for block in audio.metadata_blocks:
                            if isinstance(block, Picture):
                                data = block.data
                                break
                if data:
                    self.cover_loaded.emit(fp, data)
            except Exception:
                pass

class TrackItemDelegate(QStyledItemDelegate):
    def __init__(self, app_instance, parent=None):
        super().__init__(parent)
        self.app = app_instance

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 56)

    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        progress = getattr(self.app, 'shuffle_progress', 1.0)
        if progress < 1.0:

            y_index = max(0, option.rect.y() // 56)
            delay = min(y_index * 0.04, 0.4)                   

            item_progress = (progress - delay) * (1.0 / (1.0 - delay)) if progress > delay else 0.0
            item_progress = max(0.0, min(1.0, item_progress))


            eased_progress = 1.0 - pow(1.0 - item_progress, 3)

            offset_y = (1.0 - eased_progress) * 30.0
            painter.setOpacity(eased_progress)
            painter.translate(0, offset_y)

        rect = option.rect
        fp = index.data(Qt.ItemDataRole.UserRole)
        title = index.data(Qt.ItemDataRole.DisplayRole)


        bg_color = QColor(20, 20, 30, 80)
        border_color = QColor(255, 255, 255, 15)
        text_color = QColor("#d4d4d8")

        if option.state & QStyle.StateFlag.State_Selected:
            accent = QColor(getattr(self.app, 'accent_color_str', "#8b5cf6"))
            bg_color = QColor(accent)
            bg_color.setAlpha(60)
            border_color = QColor(accent)
            border_color.setAlpha(120)
            text_color = QColor("#ffffff")
        elif option.state & QStyle.StateFlag.State_MouseOver:
            bg_color = QColor(40, 40, 50, 100)
            text_color = QColor("#ffffff")

        margin = 4
        item_rect = rect.adjusted(margin, margin, -14, -margin)


        path = QPainterPath()
        path.addRoundedRect(float(item_rect.x()), float(item_rect.y()), float(item_rect.width()), float(item_rect.height()), 8.0, 8.0)
        painter.fillPath(path, bg_color)
        painter.setPen(border_color)
        painter.drawPath(path)


        cover_size = 36
        cover_rect = QRectF(item_rect.x() + 10, item_rect.y() + (item_rect.height() - cover_size) / 2, cover_size, cover_size)
        pixmap = self.app.cover_cache.get(fp)

        if pixmap:
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            painter.drawPixmap(cover_rect, pixmap, QRectF(pixmap.rect()))
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#2a2b36"))
            painter.drawRoundedRect(cover_rect, 6.0, 6.0)


        text_rect = QRectF(cover_rect.right() + 14, item_rect.y(), item_rect.width() - 80 - cover_rect.width(), item_rect.height())
        painter.setPen(text_color)
        font = painter.font()
        font.setPointSize(13)
        painter.setFont(font)

        fm = painter.fontMetrics()
        elided_title = fm.elidedText(title, Qt.TextElideMode.ElideRight, int(text_rect.width()))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, elided_title)


        if fp in self.app.favorites:
            heart_rect = QRect(int(item_rect.right() - 28), int(item_rect.y() + (item_rect.height() - 14) / 2), 14, 14)
            c = getattr(self.app, 'accent_color_str', "#f472b6")
            heart_icon = render_svg_icon("heart_filled", c, 14)
            heart_icon.paint(painter, heart_rect)

        painter.restore()

class MusicPlayerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Musicverse")
        self.setFixedSize(960, 660)


        from PyQt6.QtGui import QColor
        self.bg_color = QColor(13, 14, 18)
        self.bg_animation = QVariantAnimation(self)
        self.bg_animation.setDuration(1200)
        self.bg_animation.valueChanged.connect(self._on_bg_color_changed)

        self.update_theme_colors(QColor("#8b5cf6"))

        self.playlist = []
        self.original_playlist = []
        self.current_index = -1
        self.is_shuffle = False
        self.is_repeat = False
        self.is_muted = False
        self.is_smart_autoplay = False
        self.previous_volume = 80
        self.favorites = []                                       
        self.custom_playlists = {}                                     

        self.cover_cache = {}                                
        self._active_threads = set()                                                              
        self.active_playlist_name = None
        self._is_playlist_mode = False
        self._last_played_fp = None
        self.smart_mode_history = []
        self.base_playlist = []                                                                   

        self.load_playlist_data()

        self.fade_timer = QTimer(self)
        self.fade_timer.timeout.connect(self._fade_step)
        self.fade_callback = None


        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.8)


        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)


        player_card = QFrame()
        player_card.setObjectName("PlayerCard")
        player_card.setFixedWidth(360)
        player_layout = QVBoxLayout(player_card)
        player_layout.setContentsMargins(0, 0, 0, 0)
        player_layout.setSpacing(16)


        self.visual_frame = QWidget()
        self.visual_frame.setObjectName("VisualFrame")
        self.visual_frame.setFixedSize(360, 360)
        self.stacked_visual = QStackedLayout(self.visual_frame)
        self.stacked_visual.setContentsMargins(0, 0, 0, 0)


        self.cover_widget = QWidget()
        self.cover_widget.setObjectName("CoverArtWidget")
        cover_layout = QVBoxLayout(self.cover_widget)
        cover_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cover_layout.setSpacing(12)

        self.disc_icon_label = FadeLabel()
        self.disc_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.disc_icon_label.setPixmapWithFade(render_svg_pixmap("disc", size=160))

        self.cover_status_label = QLabel("พร้อมเล่นเพลง")
        self.cover_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_status_label.setStyleSheet("font-size: 13px; color: #828494; font-weight: 500;")

        cover_layout.addWidget(self.disc_icon_label)
        cover_layout.addWidget(self.cover_status_label)
        self.stacked_visual.addWidget(self.cover_widget)


        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(360, 240)
        self.media_player.setVideoOutput(self.video_widget)
        self.stacked_visual.addWidget(self.video_widget)

        self.stacked_visual.setCurrentIndex(0)
        self.media_player.hasVideoChanged.connect(self.on_has_video_changed)

        player_layout.addWidget(self.visual_frame, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)


        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        self.title_label = FadeTextLabel("เลือกเพลงเพื่อเริ่มฟัง")
        self.title_label.setObjectName("MainTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(False)
        self.title_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)

        self.artist_label = FadeTextLabel("คลังเพลงในเครื่อง")
        self.artist_label.setObjectName("SubTitle")
        self.artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artist_label.setWordWrap(False)
        self.artist_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)


        self.title_label.setNextMarqueeLabel(self.artist_label, is_starter=True)
        self.artist_label.setNextMarqueeLabel(self.title_label, is_starter=False)

        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.artist_label)
        player_layout.addLayout(info_layout)


        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(12)
        self.time_label = QLabel("0:00")
        self.time_label.setObjectName("TimeLabel")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.slider = ClickableSlider(Qt.Orientation.Horizontal)
        self.slider.valueChanged.connect(self.update_time_label)
        self.slider.seek_committed.connect(self.seek_with_fade)
        self.duration_label = QLabel("0:00")
        self.duration_label.setObjectName("TimeLabel")
        self.duration_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        progress_layout.addWidget(self.time_label)
        progress_layout.addWidget(self.slider)
        progress_layout.addWidget(self.duration_label)
        player_layout.addLayout(progress_layout)


        controls_layout = QHBoxLayout()
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_layout.setSpacing(14)

        self.shuffle_btn = QPushButton()
        self.shuffle_btn.setObjectName("ModeButton")
        self.shuffle_btn.setFixedSize(36, 36)
        self.shuffle_btn.setIcon(render_svg_icon("shuffle", "#7e8091", 18))
        self.shuffle_btn.setToolTip("สุ่มเพลง (Shuffle)")
        self.shuffle_btn.clicked.connect(self.toggle_shuffle)

        self.prev_btn = QPushButton()
        self.prev_btn.setObjectName("ControlButton")
        self.prev_btn.setFixedSize(40, 40)
        self.prev_btn.setIcon(render_svg_icon("prev", "#d4d4d8", 18))
        self.prev_btn.setToolTip("เพลงก่อนหน้า")
        self.prev_btn.clicked.connect(self.play_previous)

        self.play_btn = QPushButton()
        self.play_btn.setObjectName("PlayButton")
        self.play_btn.setFixedSize(52, 52)
        self.play_btn.setIcon(render_svg_icon("play", "#ffffff", 24))
        self.play_btn.setToolTip("เล่น / หยุดชั่วคราว")
        self.play_btn.clicked.connect(self.toggle_play)

        self.next_btn = QPushButton()
        self.next_btn.setObjectName("ControlButton")
        self.next_btn.setFixedSize(40, 40)
        self.next_btn.setIcon(render_svg_icon("next", "#d4d4d8", 18))
        self.next_btn.setToolTip("เพลงถัดไป")
        self.next_btn.clicked.connect(self.play_next)

        self.repeat_btn = QPushButton()
        self.repeat_btn.setObjectName("ModeButton")
        self.repeat_btn.setFixedSize(36, 36)
        self.repeat_btn.setIcon(render_svg_icon("repeat", "#7e8091", 18))
        self.repeat_btn.setToolTip("เล่นซ้ำ (Repeat)")
        self.repeat_btn.clicked.connect(self.toggle_repeat)

        self.autoplay_btn = QPushButton()
        self.autoplay_btn.setObjectName("ModeButton")
        self.autoplay_btn.setFixedSize(36, 36)
        self.autoplay_btn.setIcon(render_svg_icon("autoplay", "#7e8091", 18))
        self.autoplay_btn.setToolTip("เล่นอัจฉริยะ (Smart Autoplay)")
        self.autoplay_btn.clicked.connect(self.toggle_autoplay)

        self.control_fav_btn = QPushButton()
        self.control_fav_btn.setObjectName("ModeButton")
        self.control_fav_btn.setFixedSize(36, 36)
        self.control_fav_btn.setIcon(render_svg_icon("heart", "#7e8091", 18))
        self.control_fav_btn.setToolTip("เพิ่ม/ลบ เพลงที่ชอบ")
        self.control_fav_btn.clicked.connect(self.toggle_current_favorite)

        controls_layout.addWidget(self.control_fav_btn)
        controls_layout.addWidget(self.shuffle_btn)
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.next_btn)
        controls_layout.addWidget(self.repeat_btn)
        controls_layout.addWidget(self.autoplay_btn)
        player_layout.addLayout(controls_layout)


        vol_layout = QHBoxLayout()
        vol_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vol_layout.setSpacing(10)
        vol_layout.addStretch()

        self.vol_btn = QPushButton()
        self.vol_btn.setObjectName("IconButton")
        self.vol_btn.setFixedSize(28, 28)
        self.vol_btn.setIcon(render_svg_icon("volume", "#7e8091", 18))
        self.vol_btn.setToolTip("ปิด/เปิดเสียง")
        self.vol_btn.clicked.connect(self.toggle_mute)

        self.vol_slider = ClickableSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setMaximum(100)
        self.vol_slider.setValue(80)
        self.vol_slider.setFixedWidth(184)                                                                                                          
        self.vol_slider.valueChanged.connect(self.set_volume)

        self.vol_dummy = QWidget()
        self.vol_dummy.setFixedSize(28, 28)

        vol_layout.addWidget(self.vol_btn)
        vol_layout.addWidget(self.vol_slider)
        vol_layout.addWidget(self.vol_dummy)
        vol_layout.addStretch()
        player_layout.addLayout(vol_layout)

        main_layout.addWidget(player_card)


        library_card = QFrame()
        library_card.setObjectName("LibraryCard")
        library_layout = QVBoxLayout(library_card)
        library_layout.setContentsMargins(10, 0, 0, 0)
        library_layout.setSpacing(14)


        self.tab_container = QWidget()
        self.tab_container.setFixedHeight(40)

        self.tab_indicator = QFrame(self.tab_container)
        self.tab_indicator.setObjectName("TabIndicator")
        self.tab_indicator.setStyleSheet("background-color: rgba(255, 255, 255, 25); border: 1px solid rgba(255, 255, 255, 40); border-radius: 9px;")

        tab_layout = QHBoxLayout(self.tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(8)

        self.tab_library = QPushButton("คลังเพลง (0)")
        self.tab_library.setObjectName("TabButton")
        self.tab_library.setProperty("active", "true")
        self.tab_library.clicked.connect(lambda: self.switch_tab(0))

        self.tab_youtube = QPushButton("ค้นหา YouTube")
        self.tab_youtube.setObjectName("TabButton")
        self.tab_youtube.setProperty("active", "false")
        self.tab_youtube.clicked.connect(lambda: self.switch_tab(1))

        self.tab_playlists = QPushButton("เพลย์ลิสต์")
        self.tab_playlists.setObjectName("TabButton")
        self.tab_playlists.setProperty("active", "false")
        self.tab_playlists.clicked.connect(lambda: self.switch_tab(2))

        self.tab_lyrics = QPushButton("เนื้อเพลง")
        self.tab_lyrics.setObjectName("TabButton")
        self.tab_lyrics.setProperty("active", "false")
        self.tab_lyrics.clicked.connect(lambda: self.switch_tab(3))

        tab_layout.addWidget(self.tab_library)
        tab_layout.addWidget(self.tab_youtube)
        tab_layout.addWidget(self.tab_playlists)
        tab_layout.addWidget(self.tab_lyrics)
        tab_layout.addStretch()

        library_layout.addWidget(self.tab_container)


        self.right_stack = QStackedLayout()


        lib_page = QWidget()
        lib_page_layout = QVBoxLayout(lib_page)
        lib_page_layout.setContentsMargins(0, 0, 0, 0)
        lib_page_layout.setSpacing(12)


        self.pl_mode_banner = QWidget()
        self.pl_mode_banner.setStyleSheet("""
            QWidget { background-color: #1e1729; border-radius: 8px;
                      border: 1px solid #5b2d9e; }
        """)
        pl_banner_layout = QHBoxLayout(self.pl_mode_banner)
        pl_banner_layout.setContentsMargins(10, 6, 8, 6)
        pl_banner_layout.setSpacing(8)
        self.pl_mode_label = QLabel(" กำลังเล่นจากเพลย์ลิสต์")
        self.pl_mode_label.setStyleSheet("color:#c084fc; font-size:12px; font-weight:600; background:transparent; border:none;")
        self.pl_restore_btn = QPushButton(" คลังทั้งหมด")
        self.pl_restore_btn.setStyleSheet("""
            QPushButton { background:#2d1f44; border:1px solid #7c3aed; border-radius:6px;
                          color:#c4b5fd; font-size:11px; padding:3px 8px; }
            QPushButton:hover { background:#3b2660; color:#fff; }
        """)
        self.pl_restore_btn.clicked.connect(self.restore_full_library)
        pl_banner_layout.addWidget(self.pl_mode_label)
        pl_banner_layout.addStretch()
        pl_banner_layout.addWidget(self.pl_restore_btn)
        self.pl_mode_banner.hide()
        lib_page_layout.addWidget(self.pl_mode_banner)


        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("ค้นหาเพลงในคลัง...")
        self.filter_input.textChanged.connect(self.filter_playlist)
        lib_page_layout.addWidget(self.filter_input)


        self.playlist_widget = QListWidget()
        self.playlist_widget.setItemDelegate(TrackItemDelegate(self))
        self.playlist_widget.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.playlist_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.playlist_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected)
        self.playlist_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.playlist_widget.customContextMenuRequested.connect(self.show_library_context_menu)
        self.playlist_widget.model().rowsMoved.connect(self.on_library_reordered)
        lib_page_layout.addWidget(self.playlist_widget, stretch=1)

        self.right_stack.addWidget(lib_page)


        yt_page = QWidget()
        yt_page_layout = QVBoxLayout(yt_page)
        yt_page_layout.setContentsMargins(0, 0, 0, 0)
        yt_page_layout.setSpacing(12)

        yt_search_row = QHBoxLayout()
        yt_search_row.setSpacing(8)
        self.yt_input = QLineEdit()
        self.yt_input.setPlaceholderText("พิมพ์ชื่อเพลงเพื่อค้นหาบน YouTube...")
        self.yt_input.returnPressed.connect(self.search_youtube)

        self.yt_btn = QPushButton("ค้นหา")
        self.yt_btn.setObjectName("AccentButton")
        self.yt_btn.setIcon(render_svg_icon("search", "#ffffff", 16))
        self.yt_btn.clicked.connect(self.search_youtube)

        yt_search_row.addWidget(self.yt_input)
        yt_search_row.addWidget(self.yt_btn)
        yt_page_layout.addLayout(yt_search_row)

        self.search_list = QListWidget()
        self.search_list.setItemDelegate(TrackItemDelegate(self))
        self.search_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.search_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.search_list.itemDoubleClicked.connect(self.download_song)
        yt_page_layout.addWidget(self.search_list, stretch=1)

        self.right_stack.addWidget(yt_page)


        pl_page = QWidget()
        pl_page_layout = QVBoxLayout(pl_page)
        pl_page_layout.setContentsMargins(0, 0, 0, 0)
        pl_page_layout.setSpacing(10)


        pl_top_row = QHBoxLayout()
        pl_top_row.setSpacing(8)
        pl_title_lbl = QLabel("เพลย์ลิสต์ของฉัน")
        pl_title_lbl.setStyleSheet("color:#a0a0b8; font-size:12px; font-weight:600; letter-spacing:1px;")
        self.new_playlist_btn = QPushButton(" สร้างใหม่")
        self.new_playlist_btn.setObjectName("SmallBtn")
        self.new_playlist_btn.setIcon(render_svg_icon("plus", "#a0a0b0", 14))
        self.new_playlist_btn.clicked.connect(self.show_new_playlist_input)
        pl_top_row.addWidget(pl_title_lbl)
        pl_top_row.addStretch()
        pl_top_row.addWidget(self.new_playlist_btn)
        pl_page_layout.addLayout(pl_top_row)


        self.inline_input_mode = None                       
        self.inline_input_target = None
        self.new_playlist_input = QLineEdit()
        self.new_playlist_input.setPlaceholderText("ชื่อเพลย์ลิสต์ใหม่")
        self.new_playlist_input.hide()
        self.new_playlist_input.returnPressed.connect(self.commit_inline_input)
        pl_page_layout.addWidget(self.new_playlist_input)


        self.fav_btn = QPushButton()
        self.fav_btn.setObjectName("PlaylistNameBtn")
        self.fav_btn.setIcon(render_svg_icon("heart_filled", "#f472b6", 16))
        self.fav_btn.setText("    เพลงที่ชอบ (0)")
        self.fav_btn.clicked.connect(lambda: self.open_playlist_detail("__favorites__"))
        pl_page_layout.addWidget(self.fav_btn)


        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("border: none; border-top: 1px solid #23242e; margin: 2px 0;")
        pl_page_layout.addWidget(div)


        self.pl_list_widget = QListWidget()
        self.pl_list_widget.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.pl_list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.pl_list_widget.itemDoubleClicked.connect(self.on_pl_list_double_click)
        self.pl_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.pl_list_widget.customContextMenuRequested.connect(self.show_pl_context_menu)
        pl_page_layout.addWidget(self.pl_list_widget, stretch=1)

        self.right_stack.addWidget(pl_page)


        self.lyrics_page = QWidget()
        lyrics_layout = QVBoxLayout(self.lyrics_page)
        lyrics_layout.setContentsMargins(0, 0, 0, 0)
        lyrics_layout.setSpacing(12)

        self.lyrics_status_label = QLabel("เริ่มเล่นเพลงเพื่อดูเนื้อร้อง")
        self.lyrics_status_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 130);
                font-size: 14px;
            }
        """)
        self.lyrics_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lyrics_scroll = QScrollArea()
        self.lyrics_scroll.setWidgetResizable(True)
        self.lyrics_scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                width: 0px;
                background: transparent;
            }
        """)
        self.lyrics_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.lyrics_container = QWidget()
        self.lyrics_container.setStyleSheet("background-color: transparent;")
        self.lyrics_vbox = QVBoxLayout(self.lyrics_container)
        self.lyrics_vbox.setContentsMargins(0, 0, 0, 0)
        self.lyrics_vbox.setSpacing(12)
        self.lyrics_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.lyrics_scroll.setWidget(self.lyrics_container)
        self.lyrics_scroll.hide()

        self.lyrics_top_bar = QHBoxLayout()
        self.lyrics_top_bar.addStretch()

        self.lyrics_ai_btn = QPushButton("ใช้ AI แกะเนื้อเพลง")
        self.lyrics_ai_btn.setObjectName("AccentButton")
        self.lyrics_ai_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: rgba(255, 255, 255, 120);
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 12px;
            }
            QPushButton:hover { 
                background-color: rgba(255, 255, 255, 20); 
                color: white;
            }
        """)
        self.lyrics_ai_btn.hide()
        self.lyrics_ai_btn.clicked.connect(self.force_ai_transcription)

        self.lyrics_top_bar.addWidget(self.lyrics_ai_btn)


        self.lyric_sync_offset_ms = 0

        sync_btn_style = """
            QPushButton {
                background-color: transparent;
                color: rgba(255, 255, 255, 120);
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: rgba(255, 255, 255, 20); 
                color: white;
            }
        """

        self.sync_minus_btn = QPushButton("-")
        self.sync_minus_btn.setFixedSize(30, 24)
        self.sync_minus_btn.setStyleSheet(sync_btn_style)
        self.sync_minus_btn.clicked.connect(lambda: self.adjust_lyric_sync(-500))
        self.sync_minus_btn.hide()

        self.sync_label = QLabel("Sync: 0.0s")
        self.sync_label.setStyleSheet("color: rgba(255, 255, 255, 120); font-size: 12px;")
        self.sync_label.hide()

        self.sync_plus_btn = QPushButton("+")
        self.sync_plus_btn.setFixedSize(30, 24)
        self.sync_plus_btn.setStyleSheet(sync_btn_style)
        self.sync_plus_btn.clicked.connect(lambda: self.adjust_lyric_sync(500))
        self.sync_plus_btn.hide()

        self.lyrics_top_bar.addWidget(self.sync_minus_btn)
        self.lyrics_top_bar.addWidget(self.sync_label)
        self.lyrics_top_bar.addWidget(self.sync_plus_btn)

        lyrics_layout.addLayout(self.lyrics_top_bar)
        lyrics_layout.addWidget(self.lyrics_status_label)
        lyrics_layout.addWidget(self.lyrics_scroll)

        self.right_stack.addWidget(self.lyrics_page)


        self.pl_detail_page = QWidget()
        pl_detail_layout = QVBoxLayout(self.pl_detail_page)
        pl_detail_layout.setContentsMargins(0, 0, 0, 0)
        pl_detail_layout.setSpacing(10)

        detail_hdr = QHBoxLayout()
        back_btn = QPushButton("◀ กลับ")
        back_btn.setStyleSheet("""
            QPushButton { background:transparent; color:#c4b5fd; font-size:12px; font-weight:600; border:none; padding:4px; }
            QPushButton:hover { color:#fff; }
        """)
        back_btn.clicked.connect(lambda: self.switch_tab(2))

        self.pl_detail_title = QLabel("")
        self.pl_detail_title.setStyleSheet("font-size:16px; font-weight:700; color:#fff;")

        self.pl_detail_count = QLabel("")
        self.pl_detail_count.setStyleSheet("font-size:12px; color:#7e8091;")

        self.pl_detail_play_btn = QPushButton("▶ เล่นทั้งหมด")
        self.pl_detail_play_btn.setObjectName("AccentButton")
        self.pl_detail_play_btn.clicked.connect(self._play_all_from_detail)

        detail_hdr.addWidget(back_btn)
        detail_hdr.addSpacing(10)
        detail_hdr.addWidget(self.pl_detail_title)
        detail_hdr.addStretch()
        detail_hdr.addWidget(self.pl_detail_count)
        detail_hdr.addSpacing(10)
        detail_hdr.addWidget(self.pl_detail_play_btn)
        pl_detail_layout.addLayout(detail_hdr)

        self.pl_detail_list = QListWidget()
        self.pl_detail_list.setItemDelegate(TrackItemDelegate(self))
        self.pl_detail_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.pl_detail_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.pl_detail_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.pl_detail_list.itemDoubleClicked.connect(self._on_detail_play)
        self.pl_detail_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.pl_detail_list.customContextMenuRequested.connect(self._show_detail_context_menu)
        self.pl_detail_list.model().rowsMoved.connect(self.on_detail_list_reordered)
        pl_detail_layout.addWidget(self.pl_detail_list, stretch=1)

        self.right_stack.addWidget(self.pl_detail_page)

        library_layout.addLayout(self.right_stack, stretch=1)
        main_layout.addWidget(library_card, stretch=1)


        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.mediaStatusChanged.connect(self.media_status_changed)
        self.parsed_lyrics = []
        self.current_lyric_idx = -1


        self.load_music_folder("music")

        self.refresh_pl_list()
        self.refresh_favorites_btn()


        self.cover_loader_thread = LocalCoverArtLoaderThread([t['filepath'] for t in self.original_playlist])
        self.cover_loader_thread.cover_loaded.connect(self.on_cover_loaded)
        self.cover_loader_thread.start()


        self._cover_rescan_timer = QTimer(self)
        self._cover_rescan_timer.timeout.connect(self._rescan_missing_covers)
        self._cover_rescan_timer.start(90_000)

    def on_cover_loaded(self, filepath, data):
        pixmap = get_rounded_pixmap_from_data(data, size=72, radius=12)                                      
        if pixmap:
            self.cover_cache[filepath] = pixmap

            self.playlist_widget.viewport().update()
            if hasattr(self, 'pl_detail_list'):
                self.pl_detail_list.viewport().update()

    def _rescan_missing_covers(self):
        """Re-scan files that still have no cover cached (picks up newly embedded covers)."""
        missing = [t['filepath'] for t in self.original_playlist
                   if t['filepath'] not in self.cover_cache]
        if not missing:
            self._cover_rescan_timer.stop()                                      
            return
        if hasattr(self, '_rescan_thread') and self._rescan_thread.isRunning():
            return                                   
        self._rescan_thread = LocalCoverArtLoaderThread(missing)
        self._rescan_thread.cover_loaded.connect(self.on_cover_loaded)
        self._rescan_thread.start()
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'tab_indicator'):
            tabs = [self.tab_library, self.tab_youtube, self.tab_playlists]
            idx = self.right_stack.currentIndex()
            if 0 <= idx < len(tabs):
                self.tab_indicator.setGeometry(tabs[idx].geometry())

    def showEvent(self, event):
        super().showEvent(event)

        if hasattr(self, 'tab_indicator'):
            tabs = [self.tab_library, self.tab_youtube, self.tab_playlists]
            idx = self.right_stack.currentIndex()
            if 0 <= idx < len(tabs):
                self.tab_indicator.setGeometry(tabs[idx].geometry())

    def switch_tab(self, index):
        stack_idx = index
        if index == 3:
            stack_idx = 3                                   
        self.right_stack.setCurrentIndex(stack_idx)
        tabs = [self.tab_library, self.tab_youtube, self.tab_playlists, getattr(self, 'tab_lyrics', None)]


        if hasattr(self, 'tab_indicator'):
            target_tab = tabs[index]
            target_geom = target_tab.geometry()


            if target_geom.width() > 0:
                self.tab_indicator.show()
                from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
                self._indicator_anim = QPropertyAnimation(self.tab_indicator, b"geometry")
                self._indicator_anim.setDuration(300)
                self._indicator_anim.setStartValue(self.tab_indicator.geometry())
                self._indicator_anim.setEndValue(target_geom)
                self._indicator_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
                self._indicator_anim.start()
            else:

                from PyQt6.QtCore import QTimer
                QTimer.singleShot(50, lambda: self.tab_indicator.setGeometry(target_tab.geometry()))

        for i, tab in enumerate(tabs):
            tab.setProperty("active", "true" if i == index else "false")
            tab.style().unpolish(tab)
            tab.style().polish(tab)

    def on_has_video_changed(self, has_video):
        if has_video:
            self.stacked_visual.setCurrentIndex(1)
        else:
            self.stacked_visual.setCurrentIndex(0)

    def load_music_folder(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        valid_exts = {'.mp3', '.mp4', '.wav', '.m4a', '.flac', '.ogg'}
        existing_fps = {song['filepath'] for song in self.playlist}

        new_tracks = []
        for f in os.listdir(folder_path):
            if os.path.splitext(f)[1].lower() in valid_exts:
                filepath = os.path.join(folder_path, f)
                if filepath not in existing_fps:
                    title = os.path.splitext(f)[0]
                    new_tracks.append({"title": title, "filepath": filepath})

        if not new_tracks:
            return


        self.playlist.extend(new_tracks)
        self.original_playlist.extend(new_tracks)
        if not getattr(self, '_is_playlist_mode', False):
            if hasattr(self, 'base_playlist'):
                self.base_playlist.extend(new_tracks)


        self.playlist_widget.setUpdatesEnabled(False)
        for track in new_tracks:
            item = QListWidgetItem(track['title'])
            item.setToolTip(track['title'])
            item.setData(Qt.ItemDataRole.UserRole, track['filepath'])
            self.playlist_widget.addItem(item)
        self.playlist_widget.setUpdatesEnabled(True)
        self.tab_library.setText(f"คลังเพลง ({len(self.playlist):,})")

    def add_to_playlist(self, title, filepath):
        track = {"title": title, "filepath": filepath}
        self.original_playlist.append(track)
        if hasattr(self, 'base_playlist') and not getattr(self, '_is_playlist_mode', False):
            self.base_playlist.append(track)

        if not getattr(self, '_is_playlist_mode', False):
            self.playlist.append(track)
            item = QListWidgetItem(title)
            item.setToolTip(title)
            item.setData(Qt.ItemDataRole.UserRole, filepath)
            self.playlist_widget.addItem(item)
            self.tab_library.setText(f"คลังเพลง ({len(self.playlist):,})")

    def filter_playlist(self, text):
        query = text.strip().lower()
        for i in range(self.playlist_widget.count()):
            item = self.playlist_widget.item(i)
            item.setHidden(query not in item.text().lower())


    def load_playlist_data(self):
        """Load favorites and playlists from JSON file."""
        self.favorites = []
        self.custom_playlists = {}
        try:
            if os.path.exists("playlists.json"):
                with open("playlists.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.favorites = data.get("favorites", [])
                self.custom_playlists = data.get("playlists", {})
        except Exception as e:
            print(f"Error loading playlists: {e}")

    def save_playlist_data(self):
        """Save favorites and playlists to JSON file."""
        try:
            data = {
                "favorites": self.favorites,
                "playlists": self.custom_playlists
            }
            with open("playlists.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving playlists: {e}")

    def refresh_library_icons(self):
        """Force repaint to update heart icons."""
        self.playlist_widget.viewport().update()
        if hasattr(self, 'pl_detail_list'):
            self.pl_detail_list.viewport().update()

    def on_library_reordered(self, parent, start, end, destination, row):
        new_playlist = []
        for i in range(self.playlist_widget.count()):
            item = self.playlist_widget.item(i)
            new_playlist.append({"title": item.text(), "filepath": item.data(Qt.ItemDataRole.UserRole)})

        self.playlist = new_playlist
        if not self.filter_input.text().strip() and not getattr(self, 'is_shuffle', False):
            self.original_playlist = list(self.playlist)

    def on_detail_list_reordered(self, parent, start, end, destination, row):
        if not getattr(self, 'active_playlist_name', None):
            return

        new_tracks = []
        for i in range(self.pl_detail_list.count()):
            item = self.pl_detail_list.item(i)
            new_tracks.append(item.data(Qt.ItemDataRole.UserRole))

        if self.active_playlist_name == "__favorites__":
            self.favorites = new_tracks
        else:
            self.custom_playlists[self.active_playlist_name] = new_tracks

        self.save_playlist_data()

    def refresh_favorites_btn(self):
        """Update Favorites button label count."""
        count = len(self.favorites)
        self.fav_btn.setText(f"    เพลงที่ชอบ ({count})")

    def refresh_pl_list(self):
        """Rebuild the custom playlists list widget."""
        self.pl_list_widget.clear()
        for name, tracks in self.custom_playlists.items():
            item = QListWidgetItem(f"    {name}  ({len(tracks)} เพลง)")
            item.setData(Qt.ItemDataRole.UserRole, name)
            item.setToolTip(name)
            self.pl_list_widget.addItem(item)

    def toggle_favorite(self, filepath):
        """Toggle a track in/out of favorites."""
        if filepath in self.favorites:
            self.favorites.remove(filepath)
        else:
            self.favorites.append(filepath)
        self.refresh_library_icons()
        self.refresh_favorites_btn()
        self.save_playlist_data()

    def show_library_context_menu(self, pos):
        """Right-click context menu on library list."""
        item = self.playlist_widget.itemAt(pos)
        if not item:
            return
        filepath = item.data(Qt.ItemDataRole.UserRole)
        if not filepath:
            return

        menu = QMenu(self)
        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        menu.setStyleSheet("""
            QMenu { background: rgba(26, 27, 38, 0.75); border: 1px solid rgba(42, 43, 61, 0.8); border-radius: 12px; padding: 6px 0px; }
            QMenu::separator { background: rgba(42, 43, 61, 0.8); height: 1px; margin: 4px 12px; }
        """)

        is_fav = filepath in self.favorites
        c = getattr(self, 'accent_color_str', "#f472b6")
        create_styled_action(
            menu, 
            "heart_filled" if is_fav else "heart", 
            c if is_fav else "#d4d4d8",
            "เอาออกจากเพลงที่ชอบ" if is_fav else "เพิ่มในเพลงที่ชอบ",
            lambda checked=False, fp=filepath: self.toggle_favorite(fp)
        )

        menu.addSeparator()

        for pl_name in self.custom_playlists:
            create_styled_action(
                menu,
                "playlist_icon",
                "#c084fc",
                f"เพิ่มใน ‘{pl_name}’",
                lambda checked=False, n=pl_name, fp=filepath: self.add_to_custom_playlist(n, fp)
            )

        create_styled_action(
            menu,
            "plus",
            "#a0a0b0",
            "เพิ่มในเพลย์ลิสต์ใหม่...",
            lambda checked=False, fp=filepath: self.create_new_playlist(prefill_filepath=fp)
        )

        menu.addSeparator()

        create_styled_action(
            menu,
            "trash",
            "#ef4444",
            "ลบเพลงออกจากเครื่อง",
            lambda checked=False, fp=filepath: self.delete_song_from_device(fp)
        )

        menu.exec(self.playlist_widget.viewport().mapToGlobal(pos))

    def show_new_playlist_input(self):
        """Show the inline input field for creating a new playlist."""
        self.inline_input_mode = "create"
        self.inline_input_target = None
        self.new_playlist_input.clear()
        self.new_playlist_input.show()
        self.new_playlist_input.setFocus()

    def commit_inline_input(self):
        """Handle the Enter key press on the inline playlist input."""
        name = self.new_playlist_input.text().strip()
        if not name:
            self.new_playlist_input.hide()
            return

        if self.inline_input_mode == "create":
            if name in self.custom_playlists:


                self.new_playlist_input.hide()
                return

            self.custom_playlists[name] = []
            if self.inline_input_target:                              
                self.custom_playlists[name] = [self.inline_input_target]

        elif self.inline_input_mode == "rename":
            old_name = self.inline_input_target
            if name == old_name or name in self.custom_playlists:
                self.new_playlist_input.hide()
                return
            tracks = self.custom_playlists.pop(old_name)
            self.custom_playlists[name] = tracks

        self.save_playlist_data()
        self.refresh_pl_list()

        self.new_playlist_input.clear()
        self.new_playlist_input.hide()
        self.switch_tab(2)

    def create_new_playlist(self, prefill_filepath=None):
        """Prompt user for a new playlist name via inline input."""
        self.inline_input_mode = "create"
        self.inline_input_target = prefill_filepath
        self.new_playlist_input.clear()
        self.new_playlist_input.show()
        self.new_playlist_input.setFocus()

    def add_to_custom_playlist(self, pl_name, filepath):
        """Add a track to a custom playlist."""
        if pl_name not in self.custom_playlists:
            return
        if filepath not in self.custom_playlists[pl_name]:
            self.custom_playlists[pl_name].append(filepath)
            self.save_playlist_data()
            self.refresh_pl_list()

    def on_pl_list_double_click(self, item):
        pl_name = item.data(Qt.ItemDataRole.UserRole)
        if pl_name:
            self.open_playlist_detail(pl_name)

    def open_playlist_detail(self, pl_name):
        """Show playlist detail page."""
        if pl_name == "__favorites__":
            title = " เพลงที่ชอบ"
            filepath_list = self.favorites
        else:
            title = pl_name
            filepath_list = self.custom_playlists.get(pl_name, [])

        self._current_detail_pl_name = pl_name
        self._current_detail_fps = list(filepath_list)

        self.pl_detail_title.setText(title)
        self.pl_detail_count.setText(f"{len(filepath_list)} เพลง")

        self._rebuild_detail_list()
        self.right_stack.setCurrentIndex(4)                          

    def _rebuild_detail_list(self):
        self.pl_detail_list.clear()
        fp_map = {t['filepath']: t for t in self.original_playlist}
        for fp in self._current_detail_fps:
            track = fp_map.get(fp)
            title = track['title'] if track else fp.split('/')[-1]
            item = QListWidgetItem(title)
            item.setToolTip(fp)
            item.setData(Qt.ItemDataRole.UserRole, fp)
            self.pl_detail_list.addItem(item)

    def _play_all_from_detail(self):
        if self._current_detail_fps:
            self.load_and_play_playlist(list(self._current_detail_fps), self.pl_detail_title.text())

    def _on_detail_play(self, item):
        self.play_from_filepath(item.data(Qt.ItemDataRole.UserRole))

    def _show_detail_context_menu(self, pos):
        item = self.pl_detail_list.itemAt(pos)
        if not item:
            return
        fp = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)
        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        menu.setStyleSheet("""
            QMenu { background: rgba(26, 27, 38, 0.75); border: 1px solid rgba(42, 43, 61, 0.8); border-radius: 12px; padding: 6px 0px; }
            QMenu::separator { background: rgba(42, 43, 61, 0.8); height: 1px; margin: 4px 12px; }
        """)

        create_styled_action(
            menu,
            "play",
            "#10b981",
            "เล่นเพลงนี้",
            lambda checked=False, fp=fp: self.play_from_filepath(fp)
        )

        if self._current_detail_pl_name != "__favorites__":
            create_styled_action(
                menu,
                "trash",
                "#d4d4d8",
                "เอาออกจากเพลย์ลิสต์",
                lambda checked=False, fp=fp: self._remove_from_detail(fp)
            )
        else:
            c = getattr(self, 'accent_color_str', "#f472b6")
            create_styled_action(
                menu,
                "heart",
                c,
                "เอาออกจากเพลงที่ชอบ",
                lambda checked=False, fp=fp: self._remove_from_detail(fp)
            )

        menu.addSeparator()

        create_styled_action(
            menu,
            "trash",
            "#ef4444",
            "ลบเพลงออกจากเครื่อง",
            lambda checked=False, fp=fp: self.delete_song_from_device(fp)
        )

        menu.exec(self.pl_detail_list.viewport().mapToGlobal(pos))

    def delete_song_from_device(self, fp):
        was_playing = self._last_played_fp == fp
        if was_playing:
            self.media_player.stop()
            self._last_played_fp = None


        self.original_playlist = [t for t in self.original_playlist if t['filepath'] != fp]
        self.playlist = [t for t in self.playlist if t['filepath'] != fp]
        if hasattr(self, 'base_playlist'):
            self.base_playlist = [t for t in self.base_playlist if t['filepath'] != fp]
        self.cover_cache.pop(fp, None)


        if was_playing:
            self.current_index = min(self.current_index, len(self.playlist) - 1)
        elif self.current_index >= len(self.playlist):
            self.current_index = max(0, len(self.playlist) - 1)

        if fp in self.favorites:
            self.favorites.remove(fp)

        for pl_name, tracks in self.custom_playlists.items():
            if fp in tracks:
                tracks.remove(fp)

        self.save_playlist_data()

        if os.path.exists(fp):
            try:
                os.remove(fp)
            except Exception:
                pass


        for i in range(self.playlist_widget.count()):
            item = self.playlist_widget.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == fp:
                self.playlist_widget.takeItem(i)
                break

        self.tab_library.setText(f"คลังเพลง ({len(self.playlist):,})")
        self.filter_playlist(self.filter_input.text() if hasattr(self, 'filter_input') else "")
        if hasattr(self, 'right_stack') and self.right_stack.currentIndex() == 3:
            if getattr(self, '_current_detail_pl_name', None):
                self.open_playlist_detail(self._current_detail_pl_name)

        if was_playing:
            if self.playlist:
                self.play_current()
            else:
                self.title_label.setText("Musicverse")
                self.artist_label.setText("Ready to play")
                self.disc_icon_label.setPixmapWithFade(render_svg_pixmap("disc", size=160))
                self.cover_status_label.show()
                from PyQt6.QtGui import QColor
                self.update_theme_colors(QColor("#8b5cf6"))

    def _remove_from_detail(self, fp):
        if fp in self._current_detail_fps:
            self._current_detail_fps.remove(fp)

        if self._current_detail_pl_name == "__favorites__":
            if fp in self.favorites:
                self.favorites.remove(fp)
            self.refresh_library_icons()
        elif self._current_detail_pl_name in self.custom_playlists:
            self.custom_playlists[self._current_detail_pl_name] = list(self._current_detail_fps)


        for i in range(self.pl_detail_list.count()):
            item = self.pl_detail_list.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == fp:
                self.pl_detail_list.takeItem(i)
                break

        self.pl_detail_count.setText(f"{len(self._current_detail_fps)} เพลง")
        self.save_playlist_data()
        self.refresh_pl_list()
        self.refresh_favorites_btn()

    def play_from_filepath(self, filepath):
        """Find a track by filepath and play it."""
        for i, track in enumerate(self.playlist):
            if track['filepath'] == filepath:
                self.switch_tab(0)
                self.transition_to_track(i)
                return

    def load_and_play_playlist(self, filepath_list, pl_display_name="เพลย์ลิสต์"):
        """Load playlist's songs as the active queue and start playing."""
        if not filepath_list:
            return

        fp_map = {t['filepath']: t for t in self.original_playlist}


        new_queue = [fp_map[fp] for fp in filepath_list if fp in fp_map]
        if not new_queue:
            return


        self.base_playlist = list(new_queue)
        if getattr(self, 'is_shuffle', False):
            shuffled = list(self.base_playlist)
            random.shuffle(shuffled)
            self.playlist = shuffled
        else:
            self.playlist = list(self.base_playlist)

        self._is_playlist_mode = True


        self.playlist_widget.clear()
        for track in self.playlist:
            item = QListWidgetItem(track['title'])
            item.setToolTip(track['title'])
            item.setData(Qt.ItemDataRole.UserRole, track['filepath'])
            self.playlist_widget.addItem(item)


        self.pl_mode_label.setText(f" กำลังเล่น: {pl_display_name} ({len(new_queue)} เพลง)")
        self.pl_mode_banner.show()
        self.tab_library.setText(f"คลังเพลง ({len(self.playlist):,})")

        self.switch_tab(0)
        self.current_index = -1
        self.transition_to_track(0)

    def restore_full_library(self):
        """Restore the full original library as the play queue."""
        self.base_playlist = list(self.original_playlist)
        if getattr(self, 'is_shuffle', False):
            shuffled = list(self.base_playlist)
            random.shuffle(shuffled)
            self.playlist = shuffled
        else:
            self.playlist = list(self.base_playlist)

        self._is_playlist_mode = False


        self.playlist_widget.setUpdatesEnabled(False)
        self.playlist_widget.clear()
        for track in self.playlist:
            item = QListWidgetItem(track['title'])
            item.setToolTip(track['title'])
            item.setData(Qt.ItemDataRole.UserRole, track['filepath'])
            self.playlist_widget.addItem(item)
        self.playlist_widget.setUpdatesEnabled(True)

        self.pl_mode_banner.hide()
        self.tab_library.setText(f"คลังเพลง ({len(self.playlist):,})")


        if 0 <= self.current_index < len(self.original_playlist):
            current_fp = None

            if hasattr(self, '_last_played_fp'):
                for i, t in enumerate(self.playlist):
                    if t['filepath'] == self._last_played_fp:
                        self.current_index = i
                        self.playlist_widget.setCurrentRow(i)
                        break


    def show_pl_context_menu(self, pos):
        item = self.pl_list_widget.itemAt(pos)
        if not item:
            return
        pl_name = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background:#1a1b24; border:1px solid #313445; border-radius:8px; padding:4px; }
            QMenu::item { color:#d4d4d8; padding:8px 16px; border-radius:5px; }
            QMenu::item:selected { background:#8b5cf6; color:#fff; }
        """)
        rename_action = menu.addAction("เปลี่ยนชื่อ")
        rename_action.triggered.connect(lambda: self.rename_playlist(pl_name))
        delete_action = menu.addAction("ลบเพลย์ลิสต์")
        delete_action.triggered.connect(lambda: self.delete_playlist(pl_name))
        menu.exec(self.pl_list_widget.viewport().mapToGlobal(pos))

    def rename_playlist(self, old_name):
        self.inline_input_mode = "rename"
        self.inline_input_target = old_name
        self.new_playlist_input.setText(old_name)
        self.new_playlist_input.show()
        self.new_playlist_input.setFocus()
        self.new_playlist_input.selectAll()

    def delete_playlist(self, pl_name):
        self.custom_playlists.pop(pl_name, None)
        self.save_playlist_data()
        self.refresh_pl_list()

    def fade_volume(self, target_volume, duration_ms, callback=None):
        if self.fade_timer.isActive():
            self.fade_timer.stop()

        self.fade_start_vol = self.audio_output.volume()
        self.fade_target_vol = target_volume
        self.fade_steps = max(1, duration_ms // 20)
        self.fade_current_step = 0
        self.fade_callback = callback

        self.fade_timer.start(20)

    def _fade_step(self):
        self.fade_current_step += 1
        progress = self.fade_current_step / self.fade_steps
        current_vol = self.fade_start_vol + (self.fade_target_vol - self.fade_start_vol) * progress

        self.audio_output.setVolume(current_vol)

        if self.fade_current_step >= self.fade_steps:
            self.fade_timer.stop()
            if self.fade_callback:
                self.fade_callback()

    def transition_to_track(self, index):
        def do_play():
            self._is_animating_slider = False
            self.current_index = index
            self.play_current()

        self._is_animating_slider = True

        self.slider_anim = QPropertyAnimation(self.slider, b"value")
        self.slider_anim.setDuration(300)
        self.slider_anim.setStartValue(self.slider.value())
        self.slider_anim.setEndValue(0)
        self.slider_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.slider_anim.start()

        self.fade_volume(0, 300, do_play)

    def play_selected(self, item):
        self.transition_to_track(self.playlist_widget.row(item))

    def embed_cover_art(self, filepath, image_data):
        try:
            from mutagen.id3 import ID3, APIC, ID3NoHeaderError
            try:
                audio = ID3(filepath)
            except ID3NoHeaderError:
                audio = ID3()

            audio.delall("APIC")
            audio.add(
                APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=image_data
                )
            )
            audio.save(filepath, v2_version=3)
        except Exception as e:
            print("Error embedding cover art:", e)

    def on_cover_fetched(self, filepath, image_data):
        self.embed_cover_art(filepath, image_data)


        if 0 <= self.current_index < len(self.playlist):
            if self._last_played_fp == filepath:
                pixmap = get_rounded_pixmap_from_data(image_data, size=360, radius=20)
                if pixmap:
                    self.disc_icon_label.setPixmapWithFade(pixmap)
                    self.cover_status_label.hide()


                    new_color = get_dominant_color_from_data(image_data)
                    self.bg_animation.stop()
                    self.bg_animation.setStartValue(self.bg_color)
                    self.bg_animation.setEndValue(new_color)
                    self.bg_animation.start()
                    self.update_theme_colors(new_color)


        thumb_pixmap = get_rounded_pixmap_from_data(image_data, size=72, radius=12)
        if thumb_pixmap:
            self.cover_cache[filepath] = thumb_pixmap
            self.playlist_widget.viewport().update()
            if hasattr(self, 'pl_detail_list'):
                self.pl_detail_list.viewport().update()

    def _update_predicted_next_track(self):
        if not self.playlist:
            self._predicted_next_idx = -1
            return

        if getattr(self, 'is_repeat', False):
            self._predicted_next_idx = self.current_index
            return

        if getattr(self, 'is_smart_autoplay', False) and len(self.playlist) > 0:
            current_song = self.playlist[self.current_index]
            similar_track = self._get_similar_track(current_song)
            if similar_track and similar_track in self.playlist:
                self._predicted_next_idx = self.playlist.index(similar_track)
                return
            elif self.current_index < len(self.playlist) - 1:
                self._predicted_next_idx = self.current_index + 1
                return
            else:
                self._predicted_next_idx = 0
                return

        self._predicted_next_idx = (self.current_index + 1) % len(self.playlist)

    def _get_next_track_title(self):
        self._update_predicted_next_track()
        if not hasattr(self, '_predicted_next_idx') or self._predicted_next_idx == -1:
            return ""
        if 0 <= self._predicted_next_idx < len(self.playlist):
            return self.playlist[self._predicted_next_idx]['title']
        return ""

    def play_current(self):
        self._is_seeking = False
        if 0 <= self.current_index < len(self.playlist):
            song = self.playlist[self.current_index]


            if song['filepath'] not in self.smart_mode_history:
                self.smart_mode_history.append(song['filepath'])

                if len(self.smart_mode_history) > 200:
                    self.smart_mode_history = self.smart_mode_history[-150:]

            self.title_label.setText(song['title'])

            next_title = self._get_next_track_title()
            if next_title:
                self.artist_label.setTextWithFade(f"เพลงถัดไป: {next_title}")
            else:
                self.artist_label.setTextWithFade("กำลังเล่นจากคลังเพลง")

            self.cover_status_label.setText("กำลังเล่น")

            if not os.path.exists(song['filepath']):
                self.cover_status_label.setText("ไม่พบไฟล์เพลง")
                self.cover_status_label.show()
                return

            try:
                self.media_player.setSource(QUrl.fromLocalFile(song['filepath']))
            except Exception as e:
                print(f"Media source error: {e}")
                return

            self._last_played_fp = song['filepath']


            self.fetch_lyrics(song['title'], "")

            try:
                cover_data = extract_cover_art(song['filepath'])
            except Exception:
                cover_data = None
            pixmap = get_rounded_pixmap_from_data(cover_data, size=360, radius=20) if cover_data else None

            if pixmap:
                self.disc_icon_label.setPixmapWithFade(pixmap)
                self.cover_status_label.hide()


                new_color = get_dominant_color_from_data(cover_data)
                self.bg_animation.stop()
                self.bg_animation.setStartValue(self.bg_color)
                self.bg_animation.setEndValue(new_color)
                self.bg_animation.start()
                self.update_theme_colors(new_color)
            else:
                self.disc_icon_label.setPixmapWithFade(render_svg_pixmap("disc", size=160))
                self.cover_status_label.show()


                from PyQt6.QtGui import QColor
                self.bg_animation.stop()
                self.bg_animation.setStartValue(self.bg_color)
                self.bg_animation.setEndValue(QColor(13, 14, 18))
                self.bg_animation.start()
                self.update_theme_colors(QColor("#8b5cf6"))


                if hasattr(self, '_current_cover_fetcher') and self._current_cover_fetcher and self._current_cover_fetcher.isRunning():
                    self._current_cover_fetcher.cancel()
                    old_fetcher = self._current_cover_fetcher
                    self._active_threads.add(old_fetcher)
                    old_fetcher.finished.connect(lambda t=old_fetcher: self._active_threads.discard(t) if t in self._active_threads else None)

                self._current_cover_fetcher = CoverArtFetcherThread(song['filepath'], song['title'])
                self._current_cover_fetcher.cover_fetched.connect(self.on_cover_fetched)
                self._current_cover_fetcher.start()

            target_vol = self.vol_slider.value() / 100 if not self.is_muted else 0
            self.audio_output.setVolume(0)
            self.media_player.play()
            self.fade_volume(target_vol, 500)

            self.play_btn.setIcon(render_svg_icon("pause", "#ffffff", 24))
            self.refresh_control_icons()
            self.playlist_widget.setCurrentRow(self.current_index)

    def toggle_play(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            def do_pause():
                self.media_player.pause()
                self.play_btn.setIcon(render_svg_icon("play", "#ffffff", 24))
                self.cover_status_label.setText("หยุดชั่วคราว")
            self.fade_volume(0, 200, do_pause)
        else:
            if self.current_index == -1 and len(self.playlist) > 0:
                self.transition_to_track(0)
            else:
                target_vol = self.vol_slider.value() / 100 if not self.is_muted else 0
                self.audio_output.setVolume(0)
                self.media_player.play()
                self.fade_volume(target_vol, 200)
                self.play_btn.setIcon(render_svg_icon("pause", "#ffffff", 24))
                self.cover_status_label.setText("กำลังเล่น")


    def update_theme_colors(self, color):
        self.accent_color = color
        self.accent_color_str = color.name()

        c1 = color.name()

        c2 = color.lighter(130).name()
        h1 = color.lighter(110).name()
        h2 = color.lighter(140).name()
        p1 = color.darker(110).name()
        p2 = color.lighter(110).name()
        slider_hover = color.lighter(150).name()


        banner_bg = f"rgba({color.red()}, {color.green()}, {color.blue()}, 0.15)"
        banner_border = f"rgba({color.red()}, {color.green()}, {color.blue()}, 0.6)"
        btn_bg = f"rgba({color.red()}, {color.green()}, {color.blue()}, 0.25)"
        btn_hover = f"rgba({color.red()}, {color.green()}, {color.blue()}, 0.4)"
        btn_text = color.lighter(140).name()

        ss = f"""QMainWindow {{
                background-color: transparent;
            }}
            QWidget {{
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
            }}
            QFrame#PlayerCard, QFrame#LibraryCard {{
                background-color: transparent;
                border: none;
            }}
            QLabel {{
                color: #e4e4e7;
            }}
            QLabel#MainTitle {{
                font-size: 18px;
                font-weight: 700;
                color: #ffffff;
                padding-top: 4px;
            }}
            QLabel#SubTitle {{
                font-size: 13px;
                color: #828494;
            }}
            QLabel#TimeLabel {{
                color: #717382;
                font-size: 12px;
                font-weight: 500;
                min-width: 36px;
            }}
            QLineEdit {{
                background-color: rgba(25, 26, 34, 150);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 10px;
                padding: 9px 14px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid rgba(139, 92, 246, 200);
                background-color: rgba(30, 31, 42, 180);
            }}
            QPushButton#TabButton {{
                background-color: transparent;
                color: #7e8091;
                border: 1px solid transparent;
                border-radius: 9px;
                padding: 7px 16px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton#TabButton:hover {{
                color: #ffffff;
                background-color: rgba(0, 0, 0, 40);
            }}
            QPushButton#TabButton[active="true"] {{
                background-color: transparent;
                color: #ffffff;
                border: 1px solid transparent;
            }}
            QPushButton#AccentButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {c1}, stop:1 {c2});
                color: #ffffff;
                border-radius: 10px;
                border: none;
                padding: 9px 16px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton#AccentButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {h1}, stop:1 {h2});
            }}
            QPushButton#AccentButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {p1}, stop:1 {p2});
            }}
            QPushButton#PlayButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {c1}, stop:1 {c2});
                border-radius: 26px;
                border: none;
                padding: 0px;
                margin: 0px;
            }}
            QPushButton#PlayButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {h1}, stop:1 {h2});
            }}
            QPushButton#PlayButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {p1}, stop:1 {p2});
            }}
            QPushButton#ControlButton {{
                background-color: rgba(25, 26, 34, 150);
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 20px;
                padding: 0px;
                margin: 0px;
            }}
            QPushButton#ControlButton:hover {{
                background-color: {btn_hover};
                border-color: {banner_border};
            }}
            QPushButton#ControlButton:pressed {{
                background-color: rgba(18, 19, 24, 200);
            }}
            QPushButton#ModeButton {{
                background-color: rgba(25, 26, 34, 150);
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 18px;
                padding: 0px;
                margin: 0px;
            }}
            QPushButton#ModeButton:hover {{
                background-color: {btn_hover};
                border-color: {banner_border};
            }}
            QPushButton#ModeButton[active="true"] {{
                background-color: {btn_bg};
                border: 1px solid {c1};
            }}
            QPushButton#IconButton {{
                background: transparent;
                border: none;
                padding: 2px;
            }}
            QPushButton#IconButton:hover {{
                opacity: 0.8;
            }}
            QPushButton#SmallBtn {{
                background-color: rgba(255, 255, 255, 10);
                color: #a0a0b0;
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
            }}
            QPushButton#SmallBtn:hover {{
                background-color: rgba(255, 255, 255, 20);
                color: #ffffff;
            }}
            QPushButton#SmallBtn:pressed {{
                background-color: rgba(255, 255, 255, 5);
            }}
            QWidget#VisualFrame {{
                background-color: transparent;
                border-radius: 14px;
            }}
            QWidget#CoverArtWidget {{
                background-color: transparent;
                border-radius: 14px;
            }}
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: 0;
                padding-right: 4px;
            }}
            QListWidget::item {{
                background-color: rgba(23, 24, 32, 150);
                color: #d4d4d8;
                border-radius: 8px;
                padding: 10px 14px;
                margin-bottom: 6px;
                margin-right: 12px;
                border: 1px solid #222430;
                min-height: 44px;
                font-size: 13px;
            }}
            QListWidget::item:hover {{
                background-color: #1e202b;
                border-color: #313445;
                color: #ffffff;
            }}
            QListWidget::item:selected {{
                background-color: {btn_bg};
                color: #ffffff;
                border: 1px solid {c1};
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 0px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(255, 255, 255, 0.2);
                min-height: 36px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(255, 255, 255, 0.4);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
                border: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
            QSlider::groove:horizontal {{
                border: none;
                height: 4px;
                background: #272936;
                border-radius: 2px;
            }}
            QSlider::sub-page:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {c1}, stop:1 {c2});
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: #ffffff;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {slider_hover};
            }}
            QPushButton#PlaylistNameBtn {{
                background: transparent;
                border: none;
                color: #c4b5fd;
                font-size: 14px;
                font-weight: 700;
                text-align: left;
                padding: 2px 0px;
            }}
            QPushButton#PlaylistNameBtn:hover {{
                color: #ffffff;
            }}

            QPushButton#DangerBtn {{
                background-color: #2a1a1a;
                border: 1px solid #6b2222;
                border-radius: 8px;
                color: #f87171;
                font-size: 12px;
                padding: 5px 10px;
            }}
            QPushButton#DangerBtn:hover {{
                background-color: #3b1f1f;
                background-color: #3b1f1f;
            }}"""
        self.setStyleSheet(ss)

        if hasattr(self, 'pl_mode_banner'):
            self.pl_mode_banner.setStyleSheet(f"""
                QWidget {{ background-color: {banner_bg}; border-radius: 8px;
                          border: 1px solid {banner_border}; }}
            """)
        if hasattr(self, 'pl_restore_btn'):
            self.pl_restore_btn.setStyleSheet(f"""
                QPushButton {{ background:{btn_bg}; border:1px solid {banner_border}; border-radius:6px;
                              color:{btn_text}; font-size:11px; padding:3px 8px; }}
                QPushButton:hover {{ background:{btn_hover}; color:#fff; }}
            """)


        self.refresh_control_icons()
        if hasattr(self, 'playlist_widget'):
            self.playlist_widget.viewport().update()
        if hasattr(self, 'pl_detail_list'):
            self.pl_detail_list.viewport().update()

    def refresh_control_icons(self):
        if not hasattr(self, 'accent_color_str'): return
        c = self.accent_color_str
        if hasattr(self, 'shuffle_btn'):
            self.shuffle_btn.setIcon(render_svg_icon("shuffle", c if getattr(self, 'is_shuffle', False) else "#7e8091", 18))
        if hasattr(self, 'repeat_btn'):
            self.repeat_btn.setIcon(render_svg_icon("repeat", c if getattr(self, 'is_repeat', False) else "#7e8091", 18))
        if hasattr(self, 'autoplay_btn'):
            self.autoplay_btn.setIcon(render_svg_icon("autoplay", c if getattr(self, 'is_smart_autoplay', False) else "#7e8091", 18))
        if hasattr(self, 'control_fav_btn'):
            if getattr(self, '_last_played_fp', None) in getattr(self, 'favorites', []):
                self.control_fav_btn.setIcon(render_svg_icon("heart_filled", c, 18))
            else:
                self.control_fav_btn.setIcon(render_svg_icon("heart", "#7e8091", 18))
        if hasattr(self, 'fav_btn'):
            self.fav_btn.setIcon(render_svg_icon("heart_filled", c, 16))
        if hasattr(self, 'pl_mode_label'):
            self.pl_mode_label.setStyleSheet(f"color:{c}; font-size:12px; font-weight:600; background:transparent; border:none;")

    def toggle_current_favorite(self):
        if self._last_played_fp:
            self.toggle_favorite(self._last_played_fp)
            self.refresh_control_icons()

    def toggle_shuffle(self):
        if len(self.playlist) < 2:
            return

        self.is_shuffle = not self.is_shuffle
        c = getattr(self, 'accent_color_str', "#c084fc")
        color = c if self.is_shuffle else "#7e8091"
        self.shuffle_btn.setIcon(render_svg_icon("shuffle", color, 18))
        self.shuffle_btn.setProperty("active", "true" if self.is_shuffle else "false")
        self.shuffle_btn.style().unpolish(self.shuffle_btn)
        self.shuffle_btn.style().polish(self.shuffle_btn)

        current_song = self.playlist[self.current_index] if 0 <= self.current_index < len(self.playlist) else None


        source_playlist = self.base_playlist if getattr(self, '_is_playlist_mode', False) else self.original_playlist

        if self.is_shuffle:
            shuffled = list(source_playlist)
            random.shuffle(shuffled)
            if current_song in shuffled:
                shuffled.remove(current_song)
                shuffled.insert(0, current_song)
            self.playlist = shuffled
        else:
            self.playlist = list(source_playlist)


        self.playlist_widget.setUpdatesEnabled(False)
        self.playlist_widget.clear()
        for track in self.playlist:
            item = QListWidgetItem(track['title'])
            item.setToolTip(track['title'])
            item.setData(Qt.ItemDataRole.UserRole, track['filepath'])
            self.playlist_widget.addItem(item)
        self.playlist_widget.setUpdatesEnabled(True)

        if current_song and current_song in self.playlist:
            self.current_index = self.playlist.index(current_song)
            self.playlist_widget.setCurrentRow(self.current_index)


        next_title = self._get_next_track_title()
        if next_title:
            self.artist_label.setTextWithFade(f"เพลงถัดไป: {next_title}")


        self.shuffle_progress = 0.0
        self.shuffle_slide_anim = QVariantAnimation(self)
        self.shuffle_slide_anim.setDuration(600)                                       
        self.shuffle_slide_anim.setStartValue(0.0)
        self.shuffle_slide_anim.setEndValue(1.0)
        self.shuffle_slide_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        def on_shuffle_anim_step(val):
            self.shuffle_progress = val
            self.playlist_widget.viewport().update()

        def on_shuffle_anim_finished():
            self.shuffle_progress = 1.0
            self.playlist_widget.viewport().update()

        self.shuffle_slide_anim.valueChanged.connect(on_shuffle_anim_step)
        self.shuffle_slide_anim.finished.connect(on_shuffle_anim_finished)
        self.shuffle_slide_anim.start()

    def toggle_repeat(self):
        self.is_repeat = not self.is_repeat
        c = getattr(self, 'accent_color_str', "#c084fc")
        color = c if self.is_repeat else "#7e8091"
        self.repeat_btn.setIcon(render_svg_icon("repeat", color, 18))
        self.repeat_btn.setProperty("active", "true" if self.is_repeat else "false")
        self.repeat_btn.style().unpolish(self.repeat_btn)
        self.repeat_btn.style().polish(self.repeat_btn)


        next_title = self._get_next_track_title()
        if next_title:
            self.artist_label.setTextWithFade(f"เพลงถัดไป: {next_title}")

    def toggle_autoplay(self):
        self.is_smart_autoplay = not self.is_smart_autoplay
        c = getattr(self, 'accent_color_str', "#c084fc")
        color = c if self.is_smart_autoplay else "#7e8091"
        self.autoplay_btn.setIcon(render_svg_icon("autoplay", color, 18))
        self.autoplay_btn.setProperty("active", "true" if self.is_smart_autoplay else "false")
        self.autoplay_btn.style().unpolish(self.autoplay_btn)
        self.autoplay_btn.style().polish(self.autoplay_btn)


        next_title = self._get_next_track_title()
        if next_title:
            self.artist_label.setTextWithFade(f"เพลงถัดไป: {next_title}")

    def toggle_mute(self):
        if self.is_muted:
            self.is_muted = False
            self.set_volume(self.previous_volume)
            self.vol_slider.setValue(self.previous_volume)
            self.vol_btn.setIcon(render_svg_icon("volume", "#7e8091", 18))
        else:
            self.previous_volume = self.vol_slider.value()
            self.is_muted = True
            self.audio_output.setVolume(0)
            self.vol_slider.setValue(0)
            self.vol_btn.setIcon(render_svg_icon("volume_mute", "#d946ef", 18))

    def _on_bg_color_changed(self, color):
        self.bg_color = color
        self.update()

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter, QRadialGradient, QColor
        from PyQt6.QtCore import QPointF
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)


        painter.fillRect(self.rect(), QColor(10, 11, 16))


        gradient = QRadialGradient(QPointF(0, 0), self.width() * 1.5)

        center_color = QColor(self.bg_color)
        center_color.setAlpha(100)             
        gradient.setColorAt(0.0, center_color)

        edge_color = QColor(self.bg_color)
        edge_color.setAlpha(0)
        gradient.setColorAt(1.0, edge_color)

        painter.fillRect(self.rect(), gradient)

    def _get_similar_track(self, current_song):
        import random

        title = current_song['title']
        parts = title.split("-")


        if len(parts) > 1:
            keyword = parts[0].strip().lower()
        else:
            words = title.split()
            keyword = " ".join(words[:2]).lower() if len(words) > 1 else title.lower()


        all_tracks = getattr(self, 'original_playlist', [])
        history = getattr(self, 'smart_mode_history', [])

        candidates = []
        for track in all_tracks:

            if track['filepath'] != current_song['filepath'] and track['filepath'] not in history:
                if keyword in track['title'].lower():
                    candidates.append(track)

        if candidates:
            return random.choice(candidates)


        unplayed = [t for t in all_tracks if t['filepath'] not in history and t['filepath'] != current_song['filepath']]
        if unplayed:
            return random.choice(unplayed)


        if hasattr(self, 'smart_mode_history'):
            self.smart_mode_history.clear()
            self.smart_mode_history.append(current_song['filepath'])
        unplayed = [t for t in all_tracks if t['filepath'] != current_song['filepath']]
        if unplayed:
            return random.choice(unplayed)

        return None

    def play_next(self):
        if not self.playlist:
            return

        if hasattr(self, '_predicted_next_idx') and self._predicted_next_idx != -1:
            next_idx = self._predicted_next_idx
        else:

            next_idx = (self.current_index + 1) % len(self.playlist)

        self.transition_to_track(next_idx)

    def play_previous(self):
        if self.current_index > 0:
            self.transition_to_track(self.current_index - 1)
        elif len(self.playlist) > 0:
            self.transition_to_track(len(self.playlist) - 1)

    def update_time_label(self, position):
        self.time_label.setText(self.format_time(position))

    def seek_with_fade(self, position):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._is_seeking = True
            def do_seek():
                self.media_player.setPosition(position)
                target_vol = self.vol_slider.value() / 100 if not self.is_muted else 0
                self.fade_volume(target_vol, 200)
                self._is_seeking = False
            self.fade_volume(0, 150, do_seek)
        else:
            self.media_player.setPosition(position)

    def set_volume(self, volume):
        if volume > 0 and self.is_muted:
            self.is_muted = False
            self.vol_btn.setIcon(render_svg_icon("volume", "#7e8091", 18))
        elif volume == 0 and not self.is_muted:
            self.is_muted = True
            self.vol_btn.setIcon(render_svg_icon("volume_mute", "#d946ef", 18))
        if not hasattr(self, 'fade_timer') or not self.fade_timer.isActive():
            self.audio_output.setVolume(volume / 100)

    def seek_to_lyric(self, time_ms):
        offset = getattr(self, 'lyric_sync_offset_ms', 0)
        self.media_player.setPosition(time_ms + offset)

    def adjust_lyric_sync(self, delta_ms):
        self.lyric_sync_offset_ms += delta_ms
        sec = self.lyric_sync_offset_ms / 1000.0
        sign = "+" if sec > 0 else ""
        self.sync_label.setText(f"Sync: {sign}{sec:.1f}s")
        self.update_lyrics_sync(self.media_player.position())

    def position_changed(self, position):
        if getattr(self, '_is_seeking', False) or getattr(self, '_is_animating_slider', False):
            return

        if not self.slider.isSliderDown():
            self.slider.setValue(position)

        self.update_lyrics_sync(position)

    def update_lyrics_sync(self, position):
        if not hasattr(self, 'parsed_lyrics') or not self.parsed_lyrics or getattr(self, 'lyrics_scroll', None) is None or not self.lyrics_scroll.isVisible():
            return

        new_idx = -1
        offset = getattr(self, 'lyric_sync_offset_ms', 0)
        for i, (time_ms, _) in enumerate(self.parsed_lyrics):
            if position >= time_ms + offset:
                new_idx = i
            else:
                break

        old_idx = getattr(self, 'current_lyric_idx', -1)
        if new_idx != old_idx and new_idx != -1:
            self.current_lyric_idx = new_idx

            if hasattr(self, 'lyric_labels'):
                if hasattr(self, 'master_lyric_anim') and self.master_lyric_anim.state() == QParallelAnimationGroup.State.Running:
                    self.master_lyric_anim.stop()

                self.master_lyric_anim = QParallelAnimationGroup(self)

                for i, label in enumerate(self.lyric_labels):
                    dist = abs(i - new_idx)

                    if dist == 0:
                        target_scale = 1.0
                        target_opacity = 255.0
                    elif dist == 1:
                        target_scale = 0.69         
                        target_opacity = 160.0
                    elif dist == 2:
                        target_scale = 0.69
                        target_opacity = 80.0
                    elif dist == 3:
                        target_scale = 0.69
                        target_opacity = 30.0
                    else:
                        target_scale = 0.69
                        target_opacity = 5.0

                    if label.anim_group:
                        label.anim_group.stop()

                    label.anim_group = QParallelAnimationGroup(label)

                    anim1 = QPropertyAnimation(label, b"scale_factor", label)
                    anim1.setDuration(800)
                    anim1.setEndValue(target_scale)
                    anim1.setEasingCurve(QEasingCurve.Type.OutCubic if dist != 0 else QEasingCurve.Type.OutBack)

                    anim2 = QPropertyAnimation(label, b"opacity", label)
                    anim2.setDuration(800)
                    anim2.setEndValue(target_opacity)
                    anim2.setEasingCurve(QEasingCurve.Type.OutCubic)

                    label.anim_group.addAnimation(anim1)
                    label.anim_group.addAnimation(anim2)

                    self.master_lyric_anim.addAnimation(label.anim_group)

                self.master_lyric_anim.start()


                new_label = self.lyric_labels[new_idx]
                target_y = new_label.pos().y() + new_label.height() // 2 - self.lyrics_scroll.viewport().height() // 2
                max_y = self.lyrics_scroll.verticalScrollBar().maximum()
                target_y = max(0, min(target_y, max_y))

                if hasattr(self, 'scroll_anim'):
                    self.scroll_anim.stop()
                self.scroll_anim = QPropertyAnimation(self.lyrics_scroll.verticalScrollBar(), b"value", self)
                self.scroll_anim.setDuration(800)
                self.scroll_anim.setEndValue(target_y)
                self.scroll_anim.setEasingCurve(QEasingCurve.Type.OutQuart)
                self.scroll_anim.start()

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)
        self.duration_label.setText(self.format_time(duration))

    def media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self.is_repeat:
                self.transition_to_track(self.current_index)
            else:
                self.play_next()

    def format_time(self, ms):
        s = ms // 1000
        m, s = divmod(s, 60)
        return f"{m}:{s:02}"


    def search_youtube(self):
        query = self.yt_input.text().strip()
        if not query: return
        self.yt_btn.setEnabled(False)
        self.yt_btn.setText("ค้นหา...")
        self.search_list.clear()

        search = SearchThread(query)
        search.results_ready.connect(self.on_search_results)
        search.error_occurred.connect(self.on_search_error)
        self._active_threads.add(search)
        search.finished.connect(lambda s=search: self._active_threads.discard(s) if s in self._active_threads else None)
        search.start()

    def on_search_results(self, results):
        self.yt_btn.setEnabled(True)
        self.yt_btn.setText("ค้นหา")
        if not results:
            item = QListWidgetItem("ไม่พบเพลงที่ค้นหา")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.search_list.addItem(item)
            return

        for res in results:
            item = QListWidgetItem(res['title'])
            item.setToolTip(res['title'])
            item.setData(Qt.ItemDataRole.UserRole, res['url'])
            self.search_list.addItem(item)


        yt_loader = YouTubeCoverArtLoaderThread(results)
        yt_loader.cover_loaded.connect(self.on_yt_cover_loaded)
        self._active_threads.add(yt_loader)
        yt_loader.finished.connect(lambda t=yt_loader: self._active_threads.discard(t) if t in self._active_threads else None)
        yt_loader.start()

    @pyqtSlot(str, bytes)
    def on_yt_cover_loaded(self, url, data):
        pixmap = get_rounded_pixmap_from_data(data, size=72, radius=12)
        if pixmap:
            self.cover_cache[url] = pixmap
            self.search_list.viewport().update()

    def on_search_error(self, err):
        self.yt_btn.setEnabled(True)
        self.yt_btn.setText("ค้นหา")
        self.title_label.setText("ค้นหาไม่สำเร็จ")
        print(f"Search Error: {err}")

    def download_song(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        if not url: return
        title = item.text()


        import re, os
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title).strip().replace(' ', '_').lower()
        query_title = title.lower()

        for track in self.original_playlist:
            track_title = track['title'].lower()
            track_base = os.path.splitext(os.path.basename(track['filepath']))[0].lower()

            if (track_title == query_title or 
                track_base == safe_title or 
                track_title.replace('_', ' ') == query_title):


                self.switch_tab(0)
                if getattr(self, '_is_playlist_mode', False) or (hasattr(self, 'filter_input') and self.filter_input.text()):
                    if hasattr(self, 'filter_input'):
                        self.filter_input.clear()
                    self.restore_full_library()

                idx = -1
                for i, t in enumerate(self.playlist):
                    if t['filepath'] == track['filepath']:
                        idx = i
                        break

                if idx != -1:

                    self.switch_tab(0)

                    from PyQt6.QtWidgets import QGraphicsOpacityEffect
                    from PyQt6.QtCore import QPropertyAnimation, QEasingCurve


                    self.switch_tab(0)


                    def start_scroll():
                        scrollbar = self.playlist_widget.verticalScrollBar()
                        start_val = scrollbar.value()

                        item = self.playlist_widget.item(idx)
                        if not item:
                            self.transition_to_track(idx)
                            return


                        self.playlist_widget.setUpdatesEnabled(False)
                        self.playlist_widget.scrollToItem(item, QAbstractItemView.ScrollHint.PositionAtCenter)
                        target_val = scrollbar.value()
                        scrollbar.setValue(start_val)
                        self.playlist_widget.setUpdatesEnabled(True)

                        distance = abs(start_val - target_val)

                        duration = min(4000, 600 + int(distance * 1.0))

                        scroll_anim = QPropertyAnimation(scrollbar, b"value")
                        scroll_anim.setDuration(duration)
                        scroll_anim.setStartValue(start_val)
                        scroll_anim.setEndValue(target_val)
                        scroll_anim.setEasingCurve(QEasingCurve.Type.OutQuint)

                        self.title_label.setText(track['title'])
                        self.artist_label.setText("พบเพลงในคลัง... กำลังเลื่อนไปหา")

                        def play_duplicate():

                            val = scrollbar.value()
                            self.transition_to_track(idx)
                            scrollbar.setValue(val)

                        scroll_anim.finished.connect(play_duplicate)
                        scroll_anim.start()
                        self._scroll_anim = scroll_anim


                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(100, start_scroll)
                return

        self.title_label.setText(f"กำลังดาวน์โหลด: {title} ...")
        self.artist_label.setText("YouTube Download")

        dl_thread = DownloadThread(url, title)
        dl_thread.download_completed.connect(self.on_download_finished)
        dl_thread.error_occurred.connect(self.on_download_error)
        self._active_threads.add(dl_thread)
        dl_thread.finished.connect(lambda t=dl_thread: self._active_threads.discard(t) if t in self._active_threads else None)
        dl_thread.start()

    def on_download_finished(self, title, filepath):
        self.title_label.setText(title)
        self.artist_label.setText("ดาวน์โหลดเสร็จสิ้น")
        self.add_to_playlist(title, os.path.abspath(filepath))

        self.switch_tab(0)
        self.transition_to_track(len(self.playlist) - 1)

    def on_download_error(self, err):
        self.title_label.setText("ดาวน์โหลดไม่สำเร็จ")
        self.artist_label.setText("เกิดข้อผิดพลาด")
        print(f"Download Error: {err}")


    def _show_lyrics_status(self, msg):
        if hasattr(self, 'lyrics_scroll'):
            self.lyrics_scroll.hide()
            self.sync_minus_btn.hide()
            self.sync_label.hide()
            self.sync_plus_btn.hide()
        self.lyrics_status_label.setText(msg)
        self.lyrics_status_label.show()

    def parse_lrc(self, lrc_text):
        parsed = []
        import re
        for line in lrc_text.strip().split('\n'):
            match = re.search(r'\[(\d+):(\d+\.\d+)\](.*)', line)
            if match:
                m = int(match.group(1))
                s = float(match.group(2))
                text = match.group(3).strip()


                metadata_tags = ['作词', '作曲', '编曲', '制作', '混音', '母带', '和声', '企划', '出品', '吉他', '监制', '弦乐']
                if any(tag in text for tag in metadata_tags) and (':' in text or '：' in text):
                    continue

                if not text:
                    text = "..."
                time_ms = int((m * 60 + s) * 1000)
                parsed.append((time_ms, text))
        return sorted(parsed, key=lambda x: x[0])

    def fetch_lyrics(self, title, artist):
        self.lyrics_ai_btn.hide()


        import re
        clean_title = re.sub(r'\(.*?\)|\[.*?\]', '', title).strip()
        self._show_lyrics_status(f"กำลังค้นหาเนื้อเพลง...\n{clean_title}")

        query = f"{clean_title} {artist}" if artist else clean_title
        self.lyric_thread = LyricsFetcherThread(query)
        self.lyric_thread.lyrics_found.connect(self.on_lyrics_found)
        self.lyric_thread.error_occurred.connect(self.on_lyrics_error)
        self._active_threads.add(self.lyric_thread)
        self.lyric_thread.finished.connect(lambda t=self.lyric_thread: self._active_threads.discard(t) if t in self._active_threads else None)
        self.lyric_thread.start()

    def on_lyrics_found(self, lrc):
        self.parsed_lyrics = self.parse_lrc(lrc)
        self.current_lyric_idx = -1

        if not self.parsed_lyrics:
            self._show_lyrics_status(lrc)                              
            self.lyrics_ai_btn.setText("เนื้อเพลงผิด? ใช้ AI แกะเนื้อแทน (อาจรอนาน)")
            self.lyrics_ai_btn.show()
            return

        self.lyrics_status_label.hide()


        while self.lyrics_vbox.count():
            child = self.lyrics_vbox.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.lyric_labels = []


        top_spacer = QWidget()
        top_spacer.setMinimumHeight(self.lyrics_scroll.height() // 2 if self.lyrics_scroll.height() > 0 else 300)
        self.lyrics_vbox.addWidget(top_spacer)

        for ms, text in self.parsed_lyrics:
            label = LyricLabel(text, ms)
            label.lyric_clicked.connect(self.seek_to_lyric)
            self.lyric_labels.append(label)
            self.lyrics_vbox.addWidget(label)


        bottom_spacer = QWidget()
        bottom_spacer.setMinimumHeight(self.lyrics_scroll.height() // 2 if self.lyrics_scroll.height() > 0 else 300)
        self.lyrics_vbox.addWidget(bottom_spacer)

        self.lyrics_scroll.show()
        self.lyrics_ai_btn.setText("ใช้ AI แกะเนื้อเพลง")
        self.lyrics_ai_btn.show()

        self.lyric_sync_offset_ms = 0
        self.sync_label.setText("Sync: 0.0s")
        self.sync_minus_btn.show()
        self.sync_label.show()
        self.sync_plus_btn.show()

    def on_ai_error(self, err):
        self._show_lyrics_status(f"AI เกิดข้อผิดพลาด:\n{err}")
        self.lyrics_ai_btn.setText("ลองใหม่อีกครั้ง")
        self.lyrics_ai_btn.show()

    def on_lyrics_error(self, err):
        self._show_lyrics_status(f"ไม่มีเนื้อเพลงสำหรับเพลงนี้\nคุณสามารถใช้ AI ช่วยแกะเนื้อร้องได้")
        self.lyrics_ai_btn.setText("ใช้ AI แกะเนื้อเพลง")
        self.lyrics_ai_btn.show()

    def force_ai_transcription(self):
        if not self._last_played_fp: return
        self.lyrics_ai_btn.hide()
        self._show_lyrics_status("กำลังเปิดใช้งานระบบ AI...")


        self.lyrics_status_label.hide()
        while self.lyrics_vbox.count():
            child = self.lyrics_vbox.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.lyric_labels = []
        self.parsed_lyrics = []
        self.current_lyric_idx = -1

        self.top_spacer = QWidget()
        self.top_spacer.setMinimumHeight(self.lyrics_scroll.height() // 2 if self.lyrics_scroll.height() > 0 else 300)
        self.lyrics_vbox.addWidget(self.top_spacer)

        self.bottom_spacer = QWidget()
        self.bottom_spacer.setMinimumHeight(self.lyrics_scroll.height() // 2 if self.lyrics_scroll.height() > 0 else 300)
        self.lyrics_vbox.addWidget(self.bottom_spacer)

        self.lyrics_scroll.show()

        self.transcriber_thread = WhisperTranscriberThread(self._last_played_fp)
        self.transcriber_thread.progress_update.connect(self._show_lyrics_status)
        self.transcriber_thread.transcription_done.connect(self.on_lyrics_found)
        self.transcriber_thread.error_occurred.connect(self.on_ai_error)
        self.transcriber_thread.lyric_line_yielded.connect(self.on_realtime_lyric_yielded)
        self._active_threads.add(self.transcriber_thread)
        self.transcriber_thread.finished.connect(lambda t=self.transcriber_thread: self._active_threads.discard(t) if t in self._active_threads else None)
        self.transcriber_thread.start()

    def on_realtime_lyric_yielded(self, time_ms, text):
        self.lyrics_status_label.hide()
        self.lyrics_scroll.show()


        self.parsed_lyrics.append((time_ms, text))


        label = LyricLabel(text, time_ms)
        label.lyric_clicked.connect(self.seek_to_lyric)
        self.lyric_labels.append(label)


        self.lyrics_vbox.insertWidget(self.lyrics_vbox.count() - 1, label)


        self.update_lyrics_sync(self.media_player.position())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayerApp()
    window.show()
    sys.exit(app.exec())
