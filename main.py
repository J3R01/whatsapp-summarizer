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

CHAT_NAME = "Tech Stocks"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

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

try:
    print("1️⃣ Launching driver...")
    try:
        driver = webdriver.Chrome( service=Service(ChromeDriverManager(driver_version="134.0.6340.0").install()),options=options)
        print("✅ Headless Chrome launched")
    except Exception as e:
        print("❌ Chrome failed to launch")
        traceback.print_exc()
        notify_error("launching Chrome", e)
        raise

    print("2️⃣ Driver launched, loading WhatsApp...")

    try:
        driver.get("https://web.whatsapp.com")
        print("🌐 WhatsApp Web loaded")
        time.sleep(5)

        if os.path.exists("cookies.pkl"):
            print("3️⃣ Found cookies.pkl, loading cookies...")
            with open("cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    driver.add_cookie(cookie)
            driver.refresh()
            time.sleep(15)
            print("4️⃣ Cookies loaded and page refreshed")
        else:
            print("❌ No cookies.pkl found, exiting after manual QR scan")
            time.sleep(60)
            pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
            driver.quit()
            print("Cookies saved. Exiting after first-time setup.")
            exit()

    except Exception as e:
        notify_error("loading WhatsApp Web or session", e)
        raise

    try:
        print("5️⃣ Searching for chat box...")
        search_box = None
        for _ in range(20):
            try:
                search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
                break
            except:
                time.sleep(1)

        if search_box:
            search_box.click()
            search_box.send_keys(CHAT_NAME)
            time.sleep(3)

            chat = driver.find_element(By.XPATH, f'//span[@title="{CHAT_NAME}"]')
            chat.click()
            time.sleep(3)
            print("6️⃣ Chat opened")
        else:
            print("❌ Search box not found")

    except Exception as e:
        notify_error("chat selection", e)
        raise

    try:
        now = datetime.now()
        run_time = now.time()

        if run_time < datetime.strptime("06:15", "%H:%M").time():
            start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_dt = now.replace(hour=6, minute=14, second=59, microsecond=0)
            title = "📊 Pre-Market Summary for Tech Stocks:"
        else:
            yday = now - timedelta(days=1)
            start_dt = yday.replace(hour=6, minute=15, second=0, microsecond=0)
            end_dt = yday.replace(hour=23, minute=59, second=59, microsecond=0)
            title = "📈 Daily Summary for Tech Stocks (Yesterday):"

        print(f"7️⃣ Start: {start_dt}")
        print(f"8️⃣ End: {end_dt}")

        messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in") or contains(@class, "message-out")]')
        print(f"9️⃣ Found {len(messages)} raw message elements")

        collected = []

        for msg in messages:
            try:
                time_el = msg.find_element(By.XPATH, './/div[@data-pre-plain-text]')
                text_el = msg.find_element(By.XPATH, './/span[@class="_11JPr selectable-text copyable-text"]')
                timestamp = time_el.get_attribute("data-pre-plain-text")
                text = text_el.text.strip()

                raw = timestamp.strip("[]").split(", ")
                msg_time = datetime.strptime(f"{raw[1]} {raw[0]}", "%m/%d/%Y %H:%M")
                if in_time_range(msg_time, start_dt, end_dt):
                    collected.append(text)
            except:
                continue

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

    try:
        driver.quit()
        print("🛑 Driver session ending.")
    except:
        pass

    try:
        if collected:
            openai.api_key = OPENAI_API_KEY
            prompt = (
                "You're analyzing a WhatsApp group chat focused on tech stocks. "
                "From the messages below, extract up to 20 concise bullet points that summarize key stock mentions, catalysts, trends, warnings, or other valuable insights. "
                "Focus on important signals, headlines, or any notable opinions shared. "
                "Avoid general chit-chat or off-topic talk. "
                "At the end, add one line: 'Market Sentiment: X% Bullish / Y% Bearish' based on the tone of the conversation.\n\n"
                + "\n".join(collected)
            )
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            summary = response['choices'][0]['message']['content']
        else:
            summary = "No messages found in the selected time range."

        print("✅ Summary ready. Sending to Discord...")
        print(summary)

    except Exception as e:
        notify_error("OpenAI summarization", e)
        raise

    try:
        requests.post(DISCORD_WEBHOOK_URL, json={
            "content": f"{title}\n\n{summary}"
        })
        print("✅ Summary sent to Discord")

    except Exception as e:
        notify_error("sending to Discord", e)
        raise

except Exception:
    try:
        driver.quit()
    except:
        pass
