#!/usr/bin/env python3
"""
Telegram Manager Tool.
Wraps the Telegram Remote Gate.
Usage:
    from telegram_manager import send_message
    send_message(chat_id, "Hello")
"""
import sys
import os
import asyncio
from pathlib import Path

# Ensure tools is in path
TOOLS_DIR = Path(__file__).parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

try:
    from context import Context
except ImportError:
    pass

# Token Resolution
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_TOKEN:
    # Try secret file (if it existed)
    ROOT = Path(__file__).parent.parent
    TOKEN_FILE = ROOT / '.gates' / 'secrets' / 'telegram' / 'bot_token.txt'
    if TOKEN_FILE.exists():
        TELEGRAM_TOKEN = TOKEN_FILE.read_text().strip()

# Initialize Gate
try:
    CTX = Context(__file__)
    tg_mod = CTX.gate('telegram_remote_gate')
    
    if TELEGRAM_TOKEN:
        GATE = tg_mod.TelegramRemoteGate(bot_token=TELEGRAM_TOKEN)
    else:
        # Initializing without token might fail or be partial
        # We allow import but warn
        GATE = None
        print("⚠️ TELEGRAM_BOT_TOKEN not found. Telegram integration disabled.")
        
except Exception as e:
    print(f"Error initializing Telegram Gate: {e}")
    GATE = None
    sys.exit(1)

def send_message(chat_id, text, parse_mode='Markdown'):
    """Sends a message via Telegram Bot"""
    if not GATE:
        print("❌ Telegram Gate not initialized (Missing Token?)")
        return None
        
    try:
        # Wrapper for async method
        return asyncio.run(GATE.send_message(chat_id, text, parse_mode))
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return None

def get_bot_info():
    """Returns bot info"""
    if not GATE: return None
    return asyncio.run(GATE.test_token())

if __name__ == "__main__":
    if len(sys.argv) > 2:
        chat_id = sys.argv[1]
        text = " ".join(sys.argv[2:])
        print(f"Sending to {chat_id}: {text}")
        send_message(chat_id, text)
    else:
        print("Telegram Manager Ready.")
