import os
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
URLS_CONFIG = os.environ.get('URLS_CONFIG', '')

STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_state(state):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error saving state: {e}")

def send_telegram_message(text):
    if not TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": str(text)}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error: {e}")

def parse_config(raw_text):
    mapping = {}
    lines = raw_text.strip().splitlines()
    for line in lines:
        line = line.strip()
        if not line or ',' not in line:
            continue
        parts = line.split(',', 1)
        url = parts[0].strip()
        identifier = parts[1].strip()
        if url and identifier:
            mapping[url] = identifier
    return mapping

urls_map = parse_config(URLS_CONFIG)
state = load_state()

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(15)

for url, secret_number in urls_map.items():
    try:
        cache_buster = int(time.time())
        driver.get(f"{url}?v={cache_buster}")
        time.sleep(3)
        
        page_source = driver.page_source
        is_live = "LIVE" in page_source
        prev_live = state.get(secret_number, False)
        
        if is_live:
            if not prev_live:
                send_telegram_message(secret_number)
            state[secret_number] = True
        else:
            state[secret_number] = False
            
    except Exception as e:
        print(f"Error: {e}")

driver.quit()
save_state(state)
