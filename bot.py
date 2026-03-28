import requests
from bs4 import BeautifulSoup
import os
import json

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DB_FILE = "history.json"

# जिलों की लिस्ट
DISTRICTS = ["ranchi", "dhanbad", "bokaro", "jamshedpur", "deoghar", "hazaribag", "giridih", "dumka", "palamu", "ramgarh"]

# 1. History लोड करना (Point 4: Duplicate Prevention)
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        history = json.load(f)
else:
    history = []

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.get(url, params={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False})

def check_updates():
    new_jobs_found = False
    
    # --- Districts & Civil Courts Monitoring (Point 3) ---
    for dist in DISTRICTS:
        url = f"https://{dist}.nic.in/notice/recruitment/"
        try:
            r = requests.get(url, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            table = soup.find('table')
            
            if table:
                rows = table.find_all('tr')[1:4] # टॉप 3 चेक करेगा
                for row in rows:
                    cols = row.find_all('td')
                    title = cols[0].text.strip()
                    
                    # Point 4: अगर यह टाइटल पहले भेज चुके हैं तो छोड़ दो
                    if title in history:
                        continue
                    
                    # Point 5: PDF Direct Link निकालना
                    pdf_link = ""
                    link_tag = row.find('a', href=True)
                    if link_tag:
                        pdf_link = link_tag['href']
                        if not pdf_link.startswith('http'):
                            pdf_link = f"https://{dist}.nic.in" + pdf_link

                    msg = f"<b>🆕 NEW UPDATE: {dist.upper()}</b>\n\n"
                    msg += f"📝 {title}\n"
                    if pdf_link:
                        msg += f"📎 <b>Direct PDF:</b> <a href='{pdf_link}'>Download Here</a>\n"
                    msg += f"🔗 <b>Page:</b> <a href='{url}'>Open Site</a>"
                    
                    send_msg(msg)
                    history.append(title)
                    new_jobs_found = True
        except:
            continue

    # High Court Specific (Point 3)
    hc_url = "https://jharkhandhighcourt.nic.in/recruitment"
    try:
        r = requests.get(hc_url)
        if "Recruitment" in r.text and "High Court" not in history:
            send_msg(f"<b>⚖️ Jharkhand High Court Update</b>\nNayi bharti check karein.\n🔗 {hc_url}")
            history.append("High Court")
            new_jobs_found = True
    except:
        pass

    # History को सुरक्षित करना (ताकि अगली बार दोबारा न भेजे)
    if new_jobs_found:
        with open(DB_FILE, "w") as f:
            json.dump(history[-100:], f) # सिर्फ आखरी 100 रिकॉर्ड्स रखेगा

if __name__ == "__main__":
    check_updates()
