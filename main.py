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
    display.start()tartup()  # Ensure the display is not already active
    print("✅ Virtual display started")
except Exception as e:isplay started")
    print("❌ Failed to start virtual display")
    traceback.print_exc()art virtual display")
    notify_error("starting virtual display", e)
    raisey_error("starting virtual display", e)
    raise
try:
    print("1⃣ Launching driver...")
    try:t("1⃣ Launching driver...")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager(
                version=DRIVER_VERSION,  # Specify the fixed driver version
                path=".wdm"  # Cache directory in the project folderversion
            ).install()),m"  # Cache directory in the project folder
            options=options
        )   options=options
        print("✅ Headless Chrome launched")
    except Exception as e:Chrome launched")
        print("❌ Chrome failed to launch")
        traceback.print_exc()d to launch")
        notify_error("launching Chrome", e)
        raisey_error("launching Chrome", e)
        raise
    print("2⃣ Driver launched, loading WhatsApp...")
    print("2⃣ Driver launched, loading WhatsApp...")
    try:
        driver.get("https://web.whatsapp.com")
        print("🌐 WhatsApp Web loaded")p.com")
        time.sleep(5)tsApp Web loaded")
        time.sleep(5)
        if os.path.exists("cookies.pkl"):
            print("3⃣ Found cookies.pkl, loading cookies...")
            with open("cookies.pkl", "rb") as f: cookies...")
                cookies = pickle.load(f)") as f:
                for cookie in cookies:f)
                    driver.add_cookie(cookie)
            driver.refresh()dd_cookie(cookie)
            time.sleep(15)()
            print("4⃣ Cookies loaded and page refreshed")
        else:rint("4⃣ Cookies loaded and page refreshed")
            print("❌ No cookies.pkl found, exiting after manual QR scan")
            time.sleep(60)okies.pkl found, exiting after manual QR scan")
            pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
            driver.quit()river.get_cookies(), open("cookies.pkl", "wb"))
            print("Cookies saved. Exiting after first-time setup.")
            exit()"Cookies saved. Exiting after first-time setup.")
            exit()
    except Exception as e:
        notify_error("loading WhatsApp Web or session", e)
        raisey_error("loading WhatsApp Web or session", e)
        raise
    try:
        print("5⃣ Searching for chat box...")
        search_box = Noneng for chat box...")
        for _ in range(20):
            try: range(20):
                search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
                breakh_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
            except:ak
                time.sleep(1)
                time.sleep(1)
        if search_box:
            search_box.click()
            search_box.send_keys(CHAT_NAME)
            time.sleep(3)nd_keys(CHAT_NAME)
            time.sleep(3)
            chat = driver.find_element(By.XPATH, f'//span[@title="{CHAT_NAME}"]')
            chat.click()r.find_element(By.XPATH, f'//span[@title="{CHAT_NAME}"]')
            time.sleep(3)
            print("6⃣ Chat opened")
        else:rint("6⃣ Chat opened")
            print("❌ Search box not found")
            print("❌ Search box not found")
    except Exception as e:
        notify_error("chat selection", e)
        raisey_error("chat selection", e)
        raise
    try:
        now = datetime.now()
        run_time = now.time()
        run_time = now.time()
        if run_time < datetime.strptime("06:15", "%H:%M").time():
            start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_dt = now.replace(hour=6, minute=14, second=59, microsecond=0)
            title = "📊 Pre-Market Summary for Tech Stocks:"9, microsecond=0)
        else:itle = "📊 Pre-Market Summary for Tech Stocks:"
            yday = now - timedelta(days=1)
            start_dt = yday.replace(hour=6, minute=15, second=0, microsecond=0)
            end_dt = yday.replace(hour=23, minute=59, second=59, microsecond=0)
            title = "📈 Daily Summary for Tech Stocks (Yesterday):"crosecond=0)
            title = "📈 Daily Summary for Tech Stocks (Yesterday):"
        print(f"7⃣ Start: {start_dt}")
        print(f"8⃣ End: {end_dt}")t}")
        print(f"8⃣ End: {end_dt}")
        messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]')
        print(f"9⃣ Found {len(messages)} raw message elements")ns(@class, "message-in") or contains(@class, "message-out")]')
        print(f"9⃣ Found {len(messages)} raw message elements")
        collected = []
        collected = []
        for msg in messages:
            try:in messages:
                time_el = msg.find_element(By.XPATH, './/div[@data-pre-plain-text]')
                text_el = msg.find_element(By.XPATH, './/span[@class="_11JPr selectable-text copyable-text"]')
                timestamp = time_el.get_attribute("data-pre-plain-text")1JPr selectable-text copyable-text"]')
                text = text_el.text.strip()ribute("data-pre-plain-text")
                text = text_el.text.strip()
                raw = timestamp.strip("[]").split(", ")
                msg_time = datetime.strptime(f"{raw[1]} {raw[0]}", "%m/%d/%Y %H:%M")
                if in_time_range(msg_time, start_dt, end_dt):0]}", "%m/%d/%Y %H:%M")
                    collected.append(text) start_dt, end_dt):
            except: collected.append(text)
                continue
                continue
        char_limit = 20000
        current_total = 00
        trimmed = []l = 0
        for msg in collected:
            if current_total + len(msg) > char_limit:
                breakt_total + len(msg) > char_limit:
            trimmed.append(msg)
            current_total += len(msg)
        collected = trimmed= len(msg)
        collected = trimmed
        print(f"🔟 Collected {len(collected)} messages")
        print(f"🔟 Collected {len(collected)} messages")
    except Exception as e:
        notify_error("message scraping", e)
        raisey_error("message scraping", e)
        raise
    try:
        driver.quit()
        print("🛍️ Driver session ending.")
    except:nt("🛍️ Driver session ending.")
        pass
        pass
    try:
        if collected:
            openai.api_key = OPENAI_API_KEY
            prompt = (_key = OPENAI_API_KEY
                "You're analyzing a WhatsApp group chat focused on tech stocks. "
                "From the messages below, extract up to 20 concise bullet points that summarize key stock mentions, catalysts, trends, warnings, or other valuable insights. "
                "Focus on important signals, headlines, or any notable opinions shared. "marize key stock mentions, catalysts, trends, warnings, or other valuable insights. "
                "Avoid general chit-chat or off-topic talk. "y notable opinions shared. "
                "At the end, add one line: 'Market Sentiment: X% Bullish / Y% Bearish' based on the tone of the conversation.\n\n"
                + "\n".join(collected)ine: 'Market Sentiment: X% Bullish / Y% Bearish' based on the tone of the conversation.\n\n"
            )   + "\n".join(collected)
            response = openai.ChatCompletion.create(
                model="gpt-4",ChatCompletion.create(
                messages=[{"role": "user", "content": prompt}]
            )   messages=[{"role": "user", "content": prompt}]
            summary = response['choices'][0]['message']['content']
        else:ummary = response['choices'][0]['message']['content']
            summary = "No messages found in the selected time range."
            summary = "No messages found in the selected time range."
        print("✅ Summary ready. Sending to Discord...")
        print(summary)ry ready. Sending to Discord...")
        print(summary)
    except Exception as e:
        notify_error("OpenAI summarization", e)
        raisey_error("OpenAI summarization", e)
        raise
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={
            "content": f"{title}\n\n{summary}"n={
        })  "content": f"{title}\n\n{summary}"
        print("✅ Summary sent to Discord")
        print("✅ Summary sent to Discord")
    except Exception as e:
        notify_error("sending to Discord", e)
        raisey_error("sending to Discord", e)
        raise
# Stop the virtual display after the script finishes
finally:he virtual display after the script finishes
    try:
        print("🛑 Stopping virtual display...")
        display.stop()ping virtual display...")
        print("✅ Virtual display stopped")
    except Exception as e:isplay stopped")
        print("❌ Failed to stop virtual display")
        traceback.print_exc()op virtual display")
        traceback.print_exc()except Exception:    try:        driver.quit()    except:        pass
except Exception:    try:        driver.quit()    except:        pass