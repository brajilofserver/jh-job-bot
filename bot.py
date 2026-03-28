import requests
from bs4 import BeautifulSoup
import os
import json

# GitHub Secrets से डेटा लेना
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# जिले और महत्वपूर्ण वेबसाइट्स
DISTRICTS = ["ranchi", "dhanbad", "bokaro", "jamshedpur", "deoghar", "hazaribag", "giridih", "dumka", "palamu", "ramgarh"]
OTHERS = {
    "JSSC Updates": "https://jssc.nic.in/whats-new",
    "JPSC Updates": "https://www.jpsc.gov.in/whats_new.php",
    "High Court": "https://jharkhandhighcourt.nic.in/recruitment"
}

# फिल्टर कीवर्ड्स (अगर आप चाहें)
KEYWORDS = ["Driver", "Peon", "Clerk", "Operator", "Teacher", "Police", "Staff"]

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.get(url, params={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True})

def check_districts():
    results = "<b>🏢 DISTRICT JOBS UPDATES</b>\n\n"
    found = False
    for dist in DISTRICTS:
        url = f"https://{dist}.nic.in/notice/recruitment/"
        try:
            r = requests.get(url, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            table = soup.find('table')
            if table:
                row = table.find_all('tr')[1]
                title = row.find_all('td')[0].text.strip()
                date = row.find_all('td')[2].text.strip()
                
                # Keywords Check (Optional)
                if any(word.lower() in title.lower() for word in KEYWORDS):
                    results += f"⭐ <b>{dist.upper()}</b>: {title}\n📅 Last Date: {date}\n🔗 <a href='{url}'>Link</a>\n\n"
                    found = True
        except:
            continue
    if found: send_msg(results)

def check_other_boards():
    msg = "<b>📢 STATE BOARD UPDATES</b>\n\n"
    for name, url in OTHERS.items():
        try:
            r = requests.get(url, timeout=15)
            # यहाँ सिर्फ चेक कर रहे हैं कि साइट चल रही है या नहीं (Simple check)
            msg += f"✅ {name}\n🔗 <a href='{url}'>Check Site</a>\n\n"
        except:
            continue
    send_msg(msg)

if __name__ == "__main__":
    # जिले चेक करें
    check_districts()
    # JSSC/JPSC चेक करें
    check_other_boards()
