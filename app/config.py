import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PORT = int(os.getenv("PORT", "10000"))
HOST = os.getenv("HOST", "0.0.0.0")

WELCOME_TEXT = (
    "Welcome To Aizen Bot ⚡️\n"
    "Please Use this /redeem Command For Get Prime video 🧑‍💻\n"
    "For Premium use This Command /premium <key>"
)
PURCHASE_TEXT = "please Purchase Premium Key For Use 🗝️"
SERVICE_ON_TEXT = "Service is ON — free users can redeem unlimited now."
SERVICE_OFF_TEXT = "Service is OFF — only one free redeem allowed."
