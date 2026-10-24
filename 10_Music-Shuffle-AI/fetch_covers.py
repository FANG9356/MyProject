
"""
fetch_covers.py  –  ไล่โหลดปกเพลงให้ครบทุกเพลงที่ยังไม่มีปก
รันด้วย: python3 fetch_covers.py
"""

import os
import re
import sys
import time
import json
import urllib.request
import urllib.parse
import urllib.error
import mutagen
from mutagen.id3 import ID3, APIC, ID3NoHeaderError
from mutagen.mp4 import MP4, MP4Cover

MUSIC_DIR = "fangB/music"
DELAY_BETWEEN_SONGS = 1.2

def has_cover(filepath):
    try:
        audio = mutagen.File(filepath)
        if audio is None: return False
        tags = audio.tags
        if tags is None: return False
        if hasattr(tags, 'keys'):
            for key in tags.keys():
                if key.startswith('APIC'): return True
        if 'covr' in tags and tags['covr']: return True
        if hasattr(audio, 'pictures') and audio.pictures: return True
        if hasattr(audio, 'metadata_blocks'):
            from mutagen.flac import Picture
            for block in audio.metadata_blocks:
                if isinstance(block, Picture): return True
    except Exception:
        pass
    return False

def fetch_image_url(title):
    clean = title
    for term in ["official", "music", "video", "lyric", "audio", "mv"]:
        clean = re.sub(rf'(?i)\b{term}\b', '', clean).strip()
    clean = re.sub(r'[\[\(].*?[\]\)]', '', clean)
    clean = re.sub(r'[^\w\s]', ' ', clean)
    clean = ' '.join(clean.split()) or title

    try:
        q = urllib.parse.quote(clean)
        url = f"https://itunes.apple.com/search?term={q}&entity=song&limit=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=6) as r:
            data = json.loads(r.read())
        if data['resultCount'] > 0:
            art = data['results'][0].get('artworkUrl100', '')
            if art:
                return art.replace('100x100bb', '600x600bb')
    except Exception:
        pass

    try:
        q = urllib.parse.quote(title)
        yt_url = f"https://www.youtube.com/results?search_query={q}"
        req = urllib.request.Request(yt_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=6) as r:
            html = r.read().decode('utf-8')
        m = re.search(r'"videoId":"([^"]+)"', html)
        if m:
            vid = m.group(1)
            for quality in ('maxresdefault', 'hqdefault'):
                img_url = f"https://i.ytimg.com/vi/{vid}/{quality}.jpg"
                try:
                    req2 = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req2, timeout=5) as r2:
                        _ = r2.read(100)
                    return img_url
                except Exception:
                    continue
    except Exception:
        pass
    return None

def download_image(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.read()
    except Exception:
        return None

def embed_cover(filepath, data):
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == '.mp3':
            try:
                tags = ID3(filepath)
            except ID3NoHeaderError:
                tags = ID3()
            tags.delall('APIC')
            tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=data))
            tags.save(filepath, v2_version=3)
            return True
        elif ext in ('.m4a', '.mp4', '.m4p'):
            audio = MP4(filepath)
            audio.tags['covr'] = [MP4Cover(data, imageformat=MP4Cover.FORMAT_JPEG)]
            audio.save()
            return True
        elif ext == '.flac':
            from mutagen.flac import FLAC, Picture
            audio = FLAC(filepath)
            pic = Picture()
            pic.type = 3
            pic.mime = 'image/jpeg'
            pic.desc = 'Cover'
            pic.data = data
            audio.clear_pictures()
            audio.add_picture(pic)
            audio.save()
            return True
    except Exception as e:
        print(f"     ฝังปกไม่สำเร็จ: {e}")
    return False

def main():
    print("=" * 60)
    print("    Musicverse Cover Art Fetcher")
    print("  ไล่โหลดและฝังปกเพลงให้ครบทุกไฟล์ใน fangB/music/")
    print("=" * 60)

    valid_exts = {'.mp3', '.m4a', '.mp4', '.flac', '.ogg', '.wav'}
    files = sorted([
        os.path.join(MUSIC_DIR, f)
        for f in os.listdir(MUSIC_DIR)
        if os.path.splitext(f)[1].lower() in valid_exts
    ])

    total = len(files)
    need_cover = [fp for fp in files if not has_cover(fp)]
    already_done = total - len(need_cover)

    print(f"\n เพลงทั้งหมด:    {total:,} เพลง")
    print(f" มีปกแล้ว:       {already_done:,} เพลง")
    print(f" ต้องโหลดปก:    {len(need_cover):,} เพลง\n")

    if not need_cover:
        print(" ทุกเพลงมีปกครบแล้ว!")
        return

    ok = 0
    fail = 0

    for i, fp in enumerate(need_cover, 1):
        title = os.path.splitext(os.path.basename(fp))[0]
        sys.stdout.write(f"[{i}/{len(need_cover)}] {title[:55]}\n")
        sys.stdout.flush()

        img_url = fetch_image_url(title)
        if not img_url:
            print(f"    หา URL ปกไม่เจอ")
            fail += 1
            time.sleep(DELAY_BETWEEN_SONGS)
            continue

        img_data = download_image(img_url)
        if not img_data:
            print(f"    ดาวน์โหลดรูปไม่สำเร็จ")
            fail += 1
            time.sleep(DELAY_BETWEEN_SONGS)
            continue

        if embed_cover(fp, img_data):
            print(f"    ฝังปกสำเร็จ ({len(img_data)//1024} KB)")
            ok += 1
        else:
            print(f"    ฝังปกไม่สำเร็จ")
            fail += 1

        time.sleep(DELAY_BETWEEN_SONGS)

    print("\n" + "=" * 60)
    print(f" สำเร็จ: {ok} เพลง    ล้มเหลว: {fail} เพลง")
    print("=" * 60)

if __name__ == "__main__":
    main()
