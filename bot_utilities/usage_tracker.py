import os
import json
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

USAGE_LIMIT_TOKENS = int(os.getenv("USAGE_LIMIT_TOKENS", 10000))  # Default fallback = 10K
WHITELISTED_USER_IDS = os.getenv("WHITELISTED_USER_IDS", "").split(",")
WHITELISTED_USER_IDS = [uid.strip() for uid in WHITELISTED_USER_IDS if uid.strip()]

USAGE_FILE = "usage.json"

def _load_usage():
    if not os.path.exists(USAGE_FILE):
        return {}
    with open(USAGE_FILE, "r") as f:
        return json.load(f)

def _save_usage(data):
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def _current_month_key():
    now = datetime.utcnow()
    return f"{now.year}-{now.month:02d}"

def get_current_usage(user_id):
    usage_data = _load_usage()
    month_key = _current_month_key()
    return usage_data.get(month_key, {}).get(str(user_id), 0)

def update_usage(user_id, token_count):
    if str(user_id) in WHITELISTED_USER_IDS:
        return  # Skip tracking for whitelisted users

    usage_data = _load_usage()
    month_key = _current_month_key()

    if month_key not in usage_data:
        usage_data[month_key] = {}

    uid = str(user_id)
    usage_data[month_key][uid] = usage_data[month_key].get(uid, 0) + token_count
    _save_usage(usage_data)

def is_user_over_limit(user_id):
    if str(user_id) in WHITELISTED_USER_IDS:
        return False
    return get_current_usage(user_id) >= USAGE_LIMIT_TOKENS

def get_usage_summary():
    usage_data = _load_usage()
    month_key = _current_month_key()
    summary = usage_data.get(month_key, {})
    return summary

def check_for_balance_command(message):
    if message.content.strip() == "!balance" and str(message.author.id) in WHITELISTED_USER_IDS:
        usage = get_current_usage(message.author.id)
        return f"🔢 Current usage: {usage:,} tokens used this month. Limit: {USAGE_LIMIT_TOKENS:,}"
    return None
