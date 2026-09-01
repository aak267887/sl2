import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
TARGET_URL = os.environ.get('TARGET_URL')

SECRET_NUMBER = "5"

def send_telegram_message(text):
    if not TOKEN or not CHAT_ID:
        print("⚠️ Telegram credentials not configured.")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": str(text)}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(15)

if TARGET_URL:
    try:
        cache_buster = int(time.time())
        driver.get(f"{TARGET_URL}?v={cache_buster}")
        
        time.sleep(3)
        page_source = driver.page_source
        
        if "LIVE" in page_source:
            send_telegram_message(SECRET_NUMBER)
            print("🟢 Profile is LIVE!")
        else:
            print("⚪ Profile is offline.")
            
    except Exception as e:
        print(f"❌ Error checking profile: {e}")

driver.quit()
