import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import cv2
import numpy as np
import pyaudio
import time
import mss
import string
import random

SERVER_HOST = '192.168.1.26'
SERVER_PORT_SCREEN = 65432
SERVER_PORT_VOICE = 65433

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

DISCORD_DARK = '#2f3136'
DISCORD_DARKER = '#202225'
DISCORD_LIGHT_TEXT = '#dcddde'
DISCORD_GREEN = '#43b581'
DISCORD_RED = '#f04747'
DISCORD_BLUE = '#7289da'
DISCORD_CHAT_BG = '#36393f'
DISCORD_CHANNEL_BG = '#2f3136'
DISCORD_USERLIST_BG = '#202225'
DISCORD_HEADER_BG = '#292b2f'
DISCORD_SELECTED_CHANNEL = '#393c43'

TARGET_FPS = 60.0
WAIT_TIME = 1.0 / TARGET_FPS
DOWNSCALE_FACTOR = 0.50
JPEG_QUALITY = 82

class DiscordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord-like App")
        self.root.geometry("1000x700")
        self.root.configure(bg=DISCORD_DARKER)

        self.screen_running = False
        self.voice_running = False

        style = ttk.Style()
        style.theme_create("discord_dark", parent="alt", settings={
            "TFrame": {"configure": {"background": DISCORD_DARKER}},
            "TLabel": {"configure": {"background": DISCORD_DARKER, "foreground": DISCORD_LIGHT_TEXT, "font": ('Arial', 10)}},
            "TButton": {"configure": {"background": DISCORD_DARK, "foreground": DISCORD_LIGHT_TEXT, "font": ('Arial', 10, 'bold'), "padding": 8},
                        "map": {"background": [('active', DISCORD_DARKER)], "foreground": [('active', DISCORD_BLUE)]}},
            "Chat.TFrame": {"configure": {"background": DISCORD_CHAT_BG}},
        })
        style.theme_use("discord_dark")

        self.root.grid_columnconfigure(0, weight=0, minsize=220)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=0, minsize=220)
        self.root.grid_rowconfigure(0, weight=1)

        self.channel_frame = ttk.Frame(self.root, style="TFrame")
        self.channel_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 1))
        self.channel_frame.configure(style="TFrame", relief="solid", borderwidth=0)

        ttk.Label(self.channel_frame, text="BUDDAHAWAY", font=('Arial', 12, 'bold'), background=DISCORD_HEADER_BG, foreground=DISCORD_LIGHT_TEXT).pack(fill=tk.X, pady=(0, 1), ipady=10)

        self.channel_list_frame = ttk.Frame(self.channel_frame, style="TFrame")
        self.channel_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.channel_list_frame.configure(style="TFrame", background=DISCORD_CHANNEL_BG)

        self.channels = ["#ทั่วไป", "#Game Project", "#โหวต", "#file", "#ประชุม"]
        self.channel_labels = {}
        for channel in self.channels:
            label = ttk.Label(self.channel_list_frame, text=channel, background=DISCORD_CHANNEL_BG, foreground=DISCORD_LIGHT_TEXT, font=('Arial', 11), padding=(10, 5))
            label.pack(fill=tk.X, pady=1)
            label.bind("<Button-1>", self.on_channel_click)
            self.channel_labels[channel] = label

        self.current_channel = self.channels[0]
        self.channel_labels[self.current_channel].configure(background=DISCORD_SELECTED_CHANNEL)

        self.chat_panel = ttk.Frame(self.root, style="TFrame")
        self.chat_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 1))
        self.chat_panel.configure(style="TFrame", background=DISCORD_CHAT_BG)
        self.chat_panel.grid_rowconfigure(1, weight=1)
        self.chat_panel.grid_columnconfigure(0, weight=1)

        self.chat_header = ttk.Label(self.chat_panel, text=f"# {self.current_channel}", font=('Arial', 14, 'bold'), background=DISCORD_HEADER_BG, foreground=DISCORD_LIGHT_TEXT, padding=(10, 10))
        self.chat_header.grid(row=0, column=0, sticky="ew", pady=(0, 1))

        self.chat_display = scrolledtext.ScrolledText(self.chat_panel, wrap=tk.WORD, height=10, bg=DISCORD_CHAT_BG, fg=DISCORD_LIGHT_TEXT, font=('Arial', 10), state='disabled', borderwidth=0, relief="flat")
        self.chat_display.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.input_frame = ttk.Frame(self.chat_panel, style="TFrame", padding=(5, 5))
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 5))
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.chat_input = tk.Entry(self.input_frame, bg=DISCORD_DARK, fg=DISCORD_LIGHT_TEXT, insertbackground=DISCORD_LIGHT_TEXT, font=('Arial', 11), borderwidth=0)
        self.chat_input.grid(row=0, column=0, sticky="ew")
        self.chat_input.bind('<Return>', self.send_message)

        self.user_frame = ttk.Frame(self.root, style="TFrame")
        self.user_frame.grid(row=0, column=2, sticky="nsew")
        self.user_frame.configure(style="TFrame", background=DISCORD_USERLIST_BG)

        ttk.Label(self.user_frame, text="ONLINE", font=('Arial', 12, 'bold'), background=DISCORD_USERLIST_BG, foreground=DISCORD_LIGHT_TEXT, padding=(10, 5)).pack(fill=tk.X, pady=(10, 5), padx=5)

        self.user_list = []
        for i in range(24):
            username = string.ascii_uppercase[i]
            self.user_list.append(username)
            ttk.Label(self.user_frame, text=username, background=DISCORD_USERLIST_BG, foreground=DISCORD_LIGHT_TEXT, font=('Arial', 11), padding=(10, 2)).pack(fill=tk.X, padx=5)

        control_frame = ttk.Frame(self.user_frame, padding="10", style="TFrame")
        control_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        self.screen_btn = ttk.Button(control_frame, text="Start Sharing Screen", command=self.toggle_screen_share)
        self.screen_btn.pack(fill=tk.X, pady=3)

        self.voice_btn = ttk.Button(control_frame, text="Start Voice Chat", command=self.toggle_voice_chat)
        self.voice_btn.pack(fill=tk.X, pady=3)

        self.status_label = ttk.Label(control_frame, text="Ready", foreground=DISCORD_GREEN, background=DISCORD_USERLIST_BG)
        self.status_label.pack(pady=5)

        self.screen_socket = None
        self.voice_socket = None
        self.pyaudio = pyaudio.PyAudio()
        self.audio_stream = self.pyaudio.open(format=FORMAT,
                                             channels=CHANNELS,
                                             rate=RATE,
                                             output=True,
                                             frames_per_buffer=CHUNK)

    def on_channel_click(self, event):
        """Handle channel selection."""
        clicked_label = event.widget
        for label in self.channel_labels.values():
            label.configure(background=DISCORD_CHANNEL_BG)
        clicked_label.configure(background=DISCORD_SELECTED_CHANNEL)
        self.current_channel = clicked_label.cget("text")
        self.chat_header.config(text=f"# {self.current_channel}")
        self.display_message(f"--- Welcome to {self.current_channel} ---", color=DISCORD_BLUE)
        self.chat_input.focus_set()

    def send_message(self, event=None):
        message = self.chat_input.get()
        if message:
            self.display_message(f"You: {message}", color=DISCORD_GREEN)
            self.chat_input.delete(0, tk.END)

    def display_message(self, message, color=DISCORD_LIGHT_TEXT):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.tag_configure("color_tag", foreground=color)
        self.chat_display.tag_add("color_tag", "end-2c linestart", "end-2c lineend")
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')

    def toggle_screen_share(self):
        if not self.screen_running:
            self.screen_running = True
            self.screen_btn.config(text="Stop Sharing Screen")
            self.status_label.config(text="Sharing...", foreground=DISCORD_GREEN)
            threading.Thread(target=self.start_screen_sender, daemon=True).start()
        else:
            self.screen_running = False
            if self.screen_socket:
                self.screen_socket.close()
            self.screen_btn.config(text="Start Sharing Screen")
            self.status_label.config(text="Stopped", foreground=DISCORD_RED)

    def start_screen_sender(self):
        try:
            self.screen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.screen_socket.connect((SERVER_HOST, SERVER_PORT_SCREEN))
            self.status_label.config(text="Connected", foreground=DISCORD_GREEN)

            with mss.mss() as sct:
                monitor = sct.monitors[1]
                new_width = int(monitor['width'] * DOWNSCALE_FACTOR)
                new_height = int(monitor['height'] * DOWNSCALE_FACTOR)

                print(f"Sharing Resolution: {new_width}x{new_height} @ {TARGET_FPS} FPS")

                while self.screen_running:
                    start_time = time.time()
                    screenshot_mss = sct.grab(monitor)
                    screenshot_np = np.array(screenshot_mss)
                    screenshot_np = cv2.cvtColor(screenshot_np, cv2.COLOR_BGRA2BGR)

                    resized_screenshot = cv2.resize(
                        screenshot_np,
                        (new_width, new_height),
                        interpolation=cv2.INTER_LINEAR
                    )

                    final_frame = resized_screenshot
                    _, buffer = cv2.imencode('.jpg', final_frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
                    data = buffer.tobytes()
                    self.screen_socket.sendall(len(data).to_bytes(4, 'big') + data)

                    elapsed_time = time.time() - start_time
                    sleep_time = WAIT_TIME - elapsed_time

                    if sleep_time > 0:
                        time.sleep(sleep_time)
        except Exception as e:
            self.status_label.config(text=f"Screen Error: {e}", foreground=DISCORD_RED)
            self.screen_running = False
            if self.screen_socket: self.screen_socket.close()

    def toggle_voice_chat(self):
        if not self.voice_running:
            self.voice_running = True
            self.voice_btn.config(text="Stop Voice Chat")
            self.status_label.config(text="Voice Chatting...", foreground=DISCORD_GREEN)
            threading.Thread(target=self.start_voice_sender, daemon=True).start()
            threading.Thread(target=self.start_voice_receiver, daemon=True).start()
        else:
            self.voice_running = False
            if self.voice_socket: self.voice_socket.close()
            self.voice_btn.config(text="Start Voice Chat")
            self.status_label.config(text="Stopped", foreground=DISCORD_RED)

    def start_voice_sender(self):
        try:
            self.voice_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.voice_socket.connect((SERVER_HOST, SERVER_PORT_VOICE))
            stream = self.pyaudio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            while self.voice_running:
                data = stream.read(CHUNK)
                self.voice_socket.sendall(data)
            stream.stop_stream()
            stream.close()
        except Exception as e:
            self.status_label.config(text=f"Voice Send Error", foreground=DISCORD_RED)
            self.voice_running = False
            if self.voice_socket: self.voice_socket.close()

    def start_voice_receiver(self):
        receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        receiver_socket.connect((SERVER_HOST, SERVER_PORT_VOICE))
        while self.voice_running:
            try:
                data = receiver_socket.recv(4096)
                if data:
                    self.audio_stream.write(data)
            except Exception as e:
                print(f"Voice Receive Error: {e}")
                break
        receiver_socket.close()

if __name__ == '__main__':
    try:
        import mss
        import pyautogui
    except ImportError:
        print("Please install required libraries: pip install mss opencv-python pillow pyaudio pyautogui")
        exit()

    root = tk.Tk()
    app = DiscordApp(root)
    root.mainloop()
