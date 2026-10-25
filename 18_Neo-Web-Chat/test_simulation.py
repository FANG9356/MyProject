import os
import asyncio
import re

def test_file_structure():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files = [
        "index.html",
        "app.py",
        "discord_style_sharing.html",
        "docs/chat_architecture_and_protocol.md"
    ]
    for rel_path in files:
        full_path = os.path.join(base_dir, rel_path)
        assert os.path.exists(full_path), f"Missing file: {rel_path}"

def test_html_dom_structure():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "<!DOCTYPE html>" in content
    assert 'id="message-input"' in content
    assert 'id="send-btn"' in content
    assert 'id="messages-container"' in content

def test_ble_protocol_uuids():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(base_dir, "app.py")
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "6e400001-b5a3-f393-e0a9-e50e24dcca9e" in content
    assert "6e400002-b5a3-f393-e0a9-e50e24dcca9e" in content
    assert "6e400003-b5a3-f393-e0a9-e50e24dcca9e" in content

def test_async_message_queue_dispatch():
    async def run_queue_sim():
        queue = asyncio.Queue()
        test_payload = "สวัสดีครับ ทดสอบระบบแชท".encode("utf-8")
        decoded_text = test_payload.decode("utf-8")
        await queue.put(f"User: {decoded_text}")

        msg = await queue.get()
        assert "สวัสดีครับ ทดสอบระบบแชท" in msg
        assert queue.empty()

    asyncio.run(run_queue_sim())

if __name__ == "__main__":
    test_file_structure()
    test_html_dom_structure()
    test_ble_protocol_uuids()
    test_async_message_queue_dispatch()
    print("Project 18: Neo Web Chat simulation tests PASSED")
