import base64
import hashlib
import hmac
import io
import json
import os
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import qrcode
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "tips.db"
PROMPTPAY_ID = os.getenv("PROMPTPAY_ID", "0812345678")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change-me")

app = FastAPI(title="Tip Desk API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

subscribers: set[threading.Event] = set()
subscriber_lock = threading.Lock()


class TipRequest(BaseModel):
    name: str = Field(default="anonymous", max_length=80)
    amount: float = Field(gt=0, le=1_000_000)
    message: str = Field(default="ขอบคุณสำหรับการสนับสนุน!", max_length=240)


class ConfirmRequest(BaseModel):
    tip_id: str


def crc16(payload: str) -> str:
    crc = 0xFFFF
    for byte in payload.encode("ascii"):
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return f"{crc:04X}"


def tlv(tag: str, value: str) -> str:
    return f"{tag}{len(value):02d}{value}"


def promptpay_payload(target: str, amount: float) -> str:
    digits = "".join(c for c in target if c.isdigit())
    if len(digits) == 10 and digits.startswith("0"):
        merchant = "0066" + digits[1:]
    elif len(digits) == 13:
        merchant = digits
    else:
        raise ValueError("PROMPTPAY_ID must be a Thai mobile number or national ID")

    merchant_account = tlv("00", "A000000677010111") + tlv("01", merchant)
    body = (
        tlv("00", "01")
        + tlv("01", "12")
        + tlv("29", merchant_account)
        + tlv("53", "764")
        + tlv("54", f"{amount:.2f}")
        + tlv("58", "TH")
        + tlv("59", "TIP DESK")
        + tlv("60", "BANGKOK")
        + "6304"
    )
    return body + crc16(body)


def make_qr_data(payload: str) -> str:
    image = qrcode.make(payload)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


@contextmanager
def db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    with db() as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS tips (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                message TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                confirmed_at INTEGER
            )"""
        )


def tip_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def publish(tip: dict[str, Any]) -> None:
    with subscriber_lock:
        events = list(subscribers)
    for event in events:
        event.tip = tip
        event.set()


def create_tip(payload: TipRequest) -> dict[str, Any]:
    tip_id = str(uuid.uuid4())
    now = int(time.time())
    with db() as connection:
        connection.execute(
            "INSERT INTO tips (id, name, amount, message, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (tip_id, payload.name.strip() or "anonymous", payload.amount, payload.message.strip(), "pending", now),
        )
    promptpay = promptpay_payload(PROMPTPAY_ID, payload.amount)
    return {
        "id": tip_id,
        "name": payload.name.strip() or "anonymous",
        "amount": payload.amount,
        "message": payload.message.strip(),
        "status": "pending",
        "created_at": now,
        "qr_data": make_qr_data(promptpay),
        "promptpay_payload": promptpay,
    }


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/config")
def config() -> dict[str, str]:
    return {"promptpay_id": PROMPTPAY_ID}


@app.post("/api/tips")
def create_tip_endpoint(payload: TipRequest) -> dict[str, Any]:
    try:
        return create_tip(payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/api/tips")
def list_tips() -> list[dict[str, Any]]:
    with db() as connection:
        rows = connection.execute(
            "SELECT id, name, amount, message, status, created_at, confirmed_at FROM tips ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
    return [tip_dict(row) for row in rows]


@app.post("/api/tips/confirm")
def confirm_tip(payload: ConfirmRequest) -> dict[str, Any]:
    now = int(time.time())
    with db() as connection:
        row = connection.execute("SELECT * FROM tips WHERE id = ?", (payload.tip_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Tip not found")
        connection.execute("UPDATE tips SET status = 'confirmed', confirmed_at = ? WHERE id = ?", (now, payload.tip_id))
        updated = connection.execute("SELECT * FROM tips WHERE id = ?", (payload.tip_id,)).fetchone()
    tip = tip_dict(updated)
    publish(tip)
    return tip


@app.post("/api/webhooks/payment")
async def payment_webhook(request: Request, x_tip_signature: str | None = Header(default=None)) -> dict[str, str]:
    raw_body = await request.body()
    expected = hmac.new(WEBHOOK_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
    if not x_tip_signature or not hmac.compare_digest(x_tip_signature, expected):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    data = json.loads(raw_body)
    tip_id = data.get("tip_id")
    if not tip_id:
        raise HTTPException(status_code=400, detail="tip_id is required")
    confirm_tip(ConfirmRequest(tip_id=tip_id))
    return {"status": "accepted"}


@app.get("/api/events")
def events() -> StreamingResponse:
    def stream():
        event = threading.Event()
        with subscriber_lock:
            subscribers.add(event)
        try:
            yield "event: ready\ndata: {}\n\n"
            while True:
                if event.wait(timeout=20):
                    tip = getattr(event, "tip", None)
                    event.clear()
                    if tip:
                        yield f"event: tip\ndata: {json.dumps(tip, ensure_ascii=False)}\n\n"
                else:
                    yield ": heartbeat\n\n"
        finally:
            with subscriber_lock:
                subscribers.discard(event)

    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})
