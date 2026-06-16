import sqlite3
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from twilio.rest import Client
import os

app = FastAPI()

# --- CORS for mobile/web access ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "alerts.db"
tokens = []  # store Expo push tokens in memory (also persisted in DB)

# --- Twilio setup (use Railway environment variables) ---
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_FROM = os.getenv("TWILIO_FROM")
twilio_client = Client(TWILIO_SID, TWILIO_AUTH)

# --- DB helper ---
def query_db(query, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
    return results

def execute_db(query, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

# --- API endpoints ---
@app.post("/register_token")
async def register_token(req: Request):
    data = await req.json()
    token = data["token"]
    tokens.append(token)
    execute_db("INSERT INTO tokens (token, registered_at) VALUES (?, datetime('now'))", (token,))
    return {"status": "registered"}

@app.get("/signals")
def get_signals():
    results = query_db("SELECT timestamp, symbol, action, confidence, price, severity FROM signals ORDER BY timestamp DESC LIMIT 20")
    return [
        {
            "timestamp": ts,
            "symbol": symbol,
            "action": action,
            "confidence": conf,
            "price": price,
            "severity": severity
        }
        for ts, symbol, action, conf, price, severity in results
    ]

@app.get("/escalation_logs")
def get_escalation_logs():
    results = query_db("SELECT timestamp, symbol, action, confidence, price, recipient, outcome FROM escalation_log ORDER BY timestamp DESC")
    return [
        {
            "timestamp": ts,
            "symbol": symbol,
            "action": action,
            "confidence": conf,
            "price": price,
            "recipient": recipient,
            "outcome": outcome
        }
        for ts, symbol, action, conf, price, recipient, outcome in results
    ]

# --- Notification helpers ---
def send_push(token, symbol, action, confidence, price, severity):
    message = {
        "to": token,
        "title": f"{symbol} {action.upper()}",
        "body": f"Confidence {confidence}% at price {price}",
        "priority": "high"
    }

    if severity == "weak":
        message["sound"] = "weak_chime.wav"
    elif severity == "strong":
        message["sound"] = "strong_buzz.wav"
    elif severity == "critical":
        message["sound"] = "critical_siren.wav"

    requests.post("https://exp.host/--/api/v2/push/send", json=message)

def send_sms(recipient, symbol, action, confidence, price):
    if not TWILIO_SID or not TWILIO_AUTH or not TWILIO_FROM:
        print("Twilio not configured")
        return
    twilio_client.messages.create(
        body=f"ALERT: {symbol} {action.upper()} (Confidence {confidence}%, Price {price})",
        from_=TWILIO_FROM,
        to=recipient
    )

def send_voice_call(recipient, symbol, action, confidence, price):
    if not TWILIO_SID or not TWILIO_AUTH or not TWILIO_FROM:
        print("Twilio not configured")
        return
    twilio_client.calls.create(
        twiml=f"<Response><Say>Critical alert: {symbol} {action.upper()} at confidence {confidence} percent, price {price}</Say></Response>",
        from_=TWILIO_FROM,
        to=recipient
    )
