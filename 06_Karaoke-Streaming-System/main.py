from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os, uvicorn, json, re, asyncio

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

if not os.path.exists("downloads"): os.makedirs("downloads")
if not os.path.exists("static"): os.makedirs("static")

app.mount("/songs", StaticFiles(directory="downloads"), name="songs")
app.mount("/static", StaticFiles(directory="static"), name="static")

class SharedState:
    command = ""
    theme_rgb = "0, 113, 227"
    current_song = "🎵 Smart Karaoke Studio"
    next_song = "-"
    is_playing = False
    thumbnail = "" 
    current_time = 0.0
    duration = 0.0
    volume = 1.0

def clean_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip().replace(' ', '_')

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("index.html", "r", encoding="utf-8") as f: return f.read()

@app.get("/remote", response_class=HTMLResponse)
async def read_remote():
    with open("remote.html", "r", encoding="utf-8") as f: return f.read()

@app.get("/remote/send")
async def send_command(cmd: str):
    SharedState.command = cmd
    return {"status": "success"}

@app.get("/remote/poll")
async def poll_command():
    cmd = SharedState.command
    SharedState.command = ""
    return {"command": cmd}

@app.get("/state/update")
async def update_state(rgb: str = None, current: str = None, next_song: str = None, playing: bool = None, thumb: str = None, time: float = None, duration: float = None, vol: float = None): 
    if rgb: SharedState.theme_rgb = rgb
    if current: SharedState.current_song = current
    if next_song: SharedState.next_song = next_song
    if playing is not None: SharedState.is_playing = playing 
    if thumb is not None: SharedState.thumbnail = thumb
    if time is not None: SharedState.current_time = time
    if duration is not None: SharedState.duration = duration
    if vol is not None: SharedState.volume = vol
    return {"status": "success"}

@app.get("/state/get")
async def get_state(): 
    return {
        "rgb": SharedState.theme_rgb, 
        "current_song": SharedState.current_song, 
        "next_song": SharedState.next_song,
        "is_playing": SharedState.is_playing,
        "thumbnail": SharedState.thumbnail,
        "current_time": SharedState.current_time,
        "duration": SharedState.duration,
        "volume": SharedState.volume
    }

@app.get("/search")
async def search_song(q: str):
    try:
        command = ["yt-dlp", "--extractor-args", "youtube:player_client=ios", f"ytsearch20:{q}", "--dump-json", "--flat-playlist", "--quiet"]
        
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            return JSONResponse(content={"error": stderr.decode()}, status_code=500)
            
        lines = stdout.decode().strip().split('\n')
        results = []
        for line in lines:
            if not line: continue
            entry = json.loads(line)
            results.append({
                "title": entry.get('title'),
                "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                "thumbnail": f"https://i.ytimg.com/vi/{entry.get('id')}/hqdefault.jpg"
            })
        return JSONResponse(content=results)
    except Exception as e: return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/add_song")
async def add_song(url: str, title: str):
    try:
        safe_title = clean_filename(title)
        filepath = f"downloads/{safe_title}.mp4"
        
        if not os.path.exists(filepath):
            print(f"\n[Backend] ⏳ กำลังโหลด MV: {title}")
            command = [
                "yt-dlp", 
                "--cookies", "cookies.txt", 
                "--remote-components", "ejs:github",
                "-f", "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4][vcodec^=avc1]/best",
                "--merge-output-format", "mp4", 
                "-o", filepath, 
                "--no-check-certificates", 
                url
            ]
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                print(f"\n======================================")
                print(f"โหลดล้มเหลว!")
                print(f"สาเหตุ:\n{stderr.decode()}")
                print(f"======================================\n")
                return JSONResponse(content={"status": "error", "message": "Download failed"})
                
            print(f"โหลดสำเร็จ พร้อมเล่น!\n")
            
        return JSONResponse(content={"status": "success", "title": safe_title})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)})

@app.get("/list_downloads")
async def list_downloads():
    path = "downloads"
    files = [f for f in os.listdir(path) if f.endswith('.mp4')]
    files.sort(key=lambda x: os.path.getctime(os.path.join(path, x)))
    return JSONResponse(content=files)

if __name__ == "__main__": 
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")