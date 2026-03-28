import requests
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DB_FILE = "history.json"

# झारखंड के सभी 24 जिले
DISTRICTS = [
    "ranchi", "dhanbad", "bokaro", "jamshedpur", "deoghar", "hazaribag", "giridih", "dumka",
    "godda", "sahibganj", "palamu", "garhwa", "latehar", "chatra", "koderma", "gumla", 
    "lohardaga", "simdega", "khunti", "ramgarh", "pakur", "jamtara", "west-singhbhum", "seraiekela"
]

if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        history = json.load(f)
else:
    history = []

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    requests.get(url, params=params)

def parse_date(date_str):
    """तारीख को Python के समझने लायक बनाने के लिए"""
    formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None

def check_updates():
    new_jobs_found = False
    today = datetime.now().date()
    
    for dist in DISTRICTS:
        url = f"https://{dist}.nic.in/notice/recruitment/"
        try:
            r = requests.get(url, timeout=20)
            soup = BeautifulSoup(r.text, 'html.parser')
            table = soup.find('table')
            
            if table:
                rows = table.find_all('tr')[1:] 
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) < 4: continue
                    
                    title = cols[0].text.strip()
                    description = cols[1].text.strip()
                    start_date_str = cols[2].text.strip()
                    end_date_str = cols[3].text.strip()
                    
                    # --- तारीख फ़िल्टर (Point 1: सिर्फ Present Data) ---
                    end_date = parse_date(end_date_str)
                    
                    # अगर तारीख नहीं मिली या Last Date बीत चुकी है, तो skip करें
                    if end_date and end_date < today:
                        continue
                    
                    # Duplicate चेक
                    unique_id = f"{dist}_{title}_{end_date_str}"
                    if unique_id in history:
                        continue
                    
                    # PDF Link
                    pdf_link = ""
                    link_tag = row.find('a', href=True)
                    if link_tag:
                        pdf_link = link_tag['href']
                        if not pdf_link.startswith('http'):
                            pdf_link = f"https://{dist}.nic.in" + pdf_link

                    # मैसेज
                    msg = f"<b>🌟 ACTIVE JOB: {dist.upper()}</b>\n\n"
                    msg += f"📝 <b>Post:</b> {title}\n"
                    if len(description) > 5:
                        msg += f"🎓 <b>Detail:</b> {description}\n"
                    
                    msg += f"📅 <b>Start:</b> {start_date_str}\n"
                    msg += f"🚫 <b>Last Date:</b> {end_date_str}\n\n"
                    
                    if pdf_link:
                        msg += f"📎 <a href='{pdf_link}'><b>Download Official PDF</b></a>\n"
                    msg += f"🔗 <a href='{url}'><b>Open Recruitment Page</b></a>"
                    
                    send_msg(msg)
                    history.append(unique_id)
                    new_jobs_found = True
        except:
            continue

    if new_jobs_found:
        with open(DB_FILE, "w") as f:
            json.dump(history[-100:], f)

if __name__ == "__main__":
    check_updates()
