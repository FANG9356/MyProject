import asyncio
import tkinter as tk
from tkinter import scrolledtext
import threading
import sys
from bleak import BleakClient, BleakScanner
SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
root = tk.Tk()
root.title("Offline BLE Chat")
chat_box = scrolledtext.ScrolledText(root, state='disabled', wrap='word')
chat_box.pack(padx=10, pady=10, expand=True, fill='both')
input_box = tk.Entry(root, width=50)
input_box.pack(padx=10, pady=5, side='left', expand=True, fill='x')
message_queue = asyncio.Queue()
client = None
is_connected = False
loop = asyncio.new_event_loop()
def update_chat_box(message, align='left'):
    chat_box.configure(state='normal')
    if align == 'right':
        chat_box.tag_configure('right', justify='right')
        chat_box.insert(tk.END, message + "\n", 'right')
    else:
        chat_box.tag_configure('left', justify='left')
        chat_box.insert(tk.END, message + "\n", 'left')
    chat_box.configure(state='disabled')
    chat_box.see(tk.END)
def notification_handler(sender, data):
    message = data.decode('utf-8')
    asyncio.get_event_loop().call_soon_threadsafe(message_queue.put_nowait, f"ESP32: {message}")
async def send_message_async():
    global client
    if not is_connected:
        update_chat_box("Error: Not connected to ESP32.")
        return
    user_message = input_box.get()
    if user_message:
        await client.write_gatt_char(RX_UUID, user_message.encode('utf-8'))
        update_chat_box(f"Me: {user_message}", 'right')
        input_box.delete(0, tk.END)
async def main():
    global client, is_connected
    update_chat_box("Searching for ESP32...")
    try:
        device = await BleakScanner.find_device_by_name("ESP32_Chat_App", timeout=20.0)
        if not device:
            update_chat_box("Could not find the ESP32. Exiting.")
            return
        update_chat_box(f"Found ESP32: {device.name} at {device.address}")
        client = BleakClient(device.address)
        await client.connect()
        is_connected = True
        update_chat_box(f"Connected to {client.address}")
        await client.start_notify(TX_UUID, notification_handler)
        update_chat_box("Connection successful! You can start typing.")
        while client.is_connected:
            await asyncio.sleep(0.1)
            try:
                message = message_queue.get_nowait()
                update_chat_box(message)
            except asyncio.QueueEmpty:
                pass
    except Exception as e:
        update_chat_box(f"An error occurred: {e}")
        update_chat_box("Disconnected. Exiting.")
    finally:
        is_connected = False
        if client and client.is_connected:
            await client.disconnect()
def start_asyncio_loop():
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
if __name__ == "__main__":
    ble_thread = threading.Thread(target=start_asyncio_loop)
    ble_thread.daemon = True
    ble_thread.start()
    send_button = tk.Button(root, text="Send", command=lambda: asyncio.run_coroutine_threadsafe(send_message_async(), loop))
    send_button.pack(padx=10, pady=5, side='right')
    root.mainloop()
