# -----------------------------
# main.py (Railway-compatible headless-only using Selenium with fixed driver version)
# -----------------------------

import os
import time
import pickle
import traceback
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import openai
import requests
from pyvirtualdisplay import Display  # Add this import

CHAT_NAME = "Tech Stocks"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

DRIVER_VERSION = "114.0.5735.90"

# Upgrade pip at the start of the script
try:
    print("⬆️ Upgrading pip...")
    os.system("pip install --upgrade pip")  # Ensure this line is properly indented
    print("✅ pip upgraded successfully")
except Exception as e:
    print("❌ Failed to upgrade pip")
    traceback.print_exc()
    notify_error("upgrading pip", e)
    raise

def notify_error(stage, err):
    requests.post(DISCORD_WEBHOOK_URL, json={
        "content": f"⚠️ Bot failed during **{stage}**:\n```{str(err)}```"
    })

def in_time_range(msg_time, start_dt, end_dt):
    return start_dt <= msg_time <= end_dt

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Start a virtual display before launching the driver
try:
    print("🖥️ Starting virtual display...")
    display = Display(visible=0, size=(1920, 1080), use_display=100)  # Use a unique display number
    display.start()  # Start the virtual display
    print("✅ Virtual display started")
except Exception as e:
    print("❌ Failed to start virtual display")
    traceback.print_exc()
    notify_error("starting virtual display", e)
    raise

try:art a virtual display before launching the driver
    print("1⃣ Launching driver...")
    driver = webdriver.Chrome(play...")
        service=Service(ChromeDriverManager(ize=(1920, 1080), use_display=100)  # Use a unique display number
            version=DRIVER_VERSION,  # Specify the fixed driver version
            path=".wdm"  # Cache directory in the project folder
        ).install()),
        options=options
    )
    print("✅ Headless Chrome launched")virtual display", e)
except Exception as e:
    print("❌ Chrome failed to launch")
    traceback.print_exc()
    notify_error("launching Chrome", e)
    raise

print("2⃣ Driver launched, loading WhatsApp...")ervice=Service(ChromeDriverManager(
try:he fixed driver version
    driver.get("https://web.whatsapp.com")e project folder
    print("🌐 WhatsApp Web loaded")    ).install()),
    time.sleep(5)
    if os.path.exists("cookies.pkl"):
        print("3⃣ Found cookies.pkl, loading cookies...")ed")
        with open("cookies.pkl", "rb") as f:as e:
            cookies = pickle.load(f))
            for cookie in cookies:
                driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(15)
        print("4⃣ Cookies loaded and page refreshed")pp...")
    else:
        print("❌ No cookies.pkl found, exiting after manual QR scan")web.whatsapp.com")
        time.sleep(60)
        pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
        driver.quit()
        print("Cookies saved. Exiting after first-time setup.")
        exit()
except Exception as e:
    notify_error("loading WhatsApp Web or session", e)
    raise
.refresh()
try:
    print("5⃣ Searching for chat box...")
    search_box = None
    for _ in range(20):rint("❌ No cookies.pkl found, exiting after manual QR scan")
        try:    time.sleep(60)
            search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]') open("cookies.pkl", "wb"))
            break
        except:saved. Exiting after first-time setup.")
            time.sleep(1)
    if search_box:
        search_box.click()
        search_box.send_keys(CHAT_NAME)
        time.sleep(3)
        chat = driver.find_element(By.XPATH, f'//span[@title="{CHAT_NAME}"]')
        chat.click()ching for chat box...")
        time.sleep(3)
        print("6⃣ Chat opened")
    else:
        print("❌ Search box not found")x = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
except Exception as e:
    notify_error("chat selection", e)
    raisep(1)

try:
    now = datetime.now()
    run_time = now.time()
    if run_time < datetime.strptime("06:15", "%H:%M").time():find_element(By.XPATH, f'//span[@title="{CHAT_NAME}"]')
        start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = now.replace(hour=6, minute=14, second=59, microsecond=0)
        title = "📊 Pre-Market Summary for Tech Stocks:"rint("6⃣ Chat opened")
    else:else:
        yday = now - timedelta(days=1)box not found")
        start_dt = yday.replace(hour=6, minute=15, second=0, microsecond=0)
        end_dt = yday.replace(hour=23, minute=59, second=59, microsecond=0)lection", e)
        title = "📈 Daily Summary for Tech Stocks (Yesterday):"
    print(f"7⃣ Start: {start_dt}")
    print(f"8⃣ End: {end_dt}")
    messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]')
    print(f"9⃣ Found {len(messages)} raw message elements")
    collected = []6:15", "%H:%M").time():
    for msg in messages:
        try:
            time_el = msg.find_element(By.XPATH, './/div[@data-pre-plain-text]')
            text_el = msg.find_element(By.XPATH, './/span[@class="_11JPr selectable-text copyable-text"]')
            timestamp = time_el.get_attribute("data-pre-plain-text")s=1)
            text = text_el.text.strip()ur=6, minute=15, second=0, microsecond=0)
            raw = timestamp.strip("[]").split(", ")hour=23, minute=59, second=59, microsecond=0)
            msg_time = datetime.strptime(f"{raw[1]} {raw[0]}", "%m/%d/%Y %H:%M")
            if in_time_range(msg_time, start_dt, end_dt):
                collected.append(text)
        except:ver.find_elements(By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]')
            continuend {len(messages)} raw message elements")
    char_limit = 20000
    current_total = 0
    trimmed = []
    for msg in collected:
        if current_total + len(msg) > char_limit:
            break
        trimmed.append(msg)
        current_total += len(msg)
    collected = trimmed
    print(f"🔟 Collected {len(collected)} messages")
except Exception as e:
    notify_error("message scraping", e)
    raise
00
try:
    driver.quit()
    print("🛍️ Driver session ending.")ted:
except:+ len(msg) > char_limit:
    pass

try:n(msg)
    if collected:
        openai.api_key = OPENAI_API_KEYlected)} messages")
        prompt = (
            "You're analyzing a WhatsApp group chat focused on tech stocks. "
            "From the messages below, extract up to 20 concise bullet points that summarize key stock mentions, catalysts, trends, warnings, or other valuable insights. "
            "Focus on important signals, headlines, or any notable opinions shared. "
            "Avoid general chit-chat or off-topic talk. "
            "At the end, add one line: 'Market Sentiment: X% Bullish / Y% Bearish' based on the tone of the conversation.\n\n"
            + "\n".join(collected)("🛍️ Driver session ending.")
        )pt:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )ollected:
        summary = response['choices'][0]['message']['content']openai.api_key = OPENAI_API_KEY
    else:    prompt = (
        summary = "No messages found in the selected time range."re analyzing a WhatsApp group chat focused on tech stocks. "
    print("✅ Summary ready. Sending to Discord...")xtract up to 20 concise bullet points that summarize key stock mentions, catalysts, trends, warnings, or other valuable insights. "
    print(summary), headlines, or any notable opinions shared. "
except Exception as e:
    notify_error("OpenAI summarization", e)
    raise

try:
    requests.post(DISCORD_WEBHOOK_URL, json={
        "content": f"{title}\n\n{summary}"er", "content": prompt}]
    })
    print("✅ Summary sent to Discord")e']['content']
except Exception as e:
    notify_error("sending to Discord", e)range."
    raise

# Stop the virtual display after the script finishes
finally:
    try:
        print("🛑 Stopping virtual display...")
        display.stop()
        print("✅ Virtual display stopped")ORD_WEBHOOK_URL, json={
    except Exception as e:
        print("❌ Failed to stop virtual display")
        traceback.print_exc()("✅ Summary sent to Discord")
    try:pt Exception as e:
        driver.quit()
    except:
        pass
except Exception:t finishes
    try:
        driver.quit()
    except:")
        pass