import requests
from bs4 import BeautifulSoup
import os
import json

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

def check_updates():
    new_jobs_found = False
    
    for dist in DISTRICTS:
        url = f"https://{dist}.nic.in/notice/recruitment/"
        try:
            r = requests.get(url, timeout=20)
            soup = BeautifulSoup(r.text, 'html.parser')
            table = soup.find('table')
            
            if table:
                rows = table.find_all('tr')[1:] # सभी Rows चेक करेगा
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) < 4: continue
                    
                    title = cols[0].text.strip()
                    description = cols[1].text.strip() # इसमें अक्सर Qualification होती है
                    start_date = cols[2].text.strip() # शुरू होने की तारीख
                    end_date = cols[3].text.strip()   # आखिरी तारीख
                    
                    # Duplicate चेक (Title + End Date का कॉम्बिनेशन ताकि डेटा सटीक रहे)
                    unique_id = f"{dist}_{title}_{end_date}"
                    if unique_id in history:
                        continue
                    
                    # PDF Link निकालना
                    pdf_link = ""
                    link_tag = row.find('a', href=True)
                    if link_tag:
                        pdf_link = link_tag['href']
                        if not pdf_link.startswith('http'):
                            pdf_link = f"https://{dist}.nic.in" + pdf_link

                    # मैसेज तैयार करना
                    msg = f"<b>🏢 DISTRICT: {dist.upper()}</b>\n\n"
                    msg += f"📝 <b>Post:</b> {title}\n"
                    
                    # अगर Description में Qualification लिखी है (जैसे 10th, Graduate, etc.)
                    if len(description) > 5:
                        msg += f"🎓 <b>Qualification/Detail:</b> {description}\n"
                    else:
                        msg += f"🎓 <b>Qualification:</b> (Check PDF for details)\n"
                        
                    msg += f"📅 <b>Start Date:</b> {start_date}\n"
                    msg += f"🚫 <b>Last Date:</b> {end_date}\n\n"
                    
                    if pdf_link:
                        msg += f"📎 <a href='{pdf_link}'><b>Download Official PDF</b></a>\n"
                    msg += f"🔗 <a href='{url}'><b>Open Recruitment Page</b></a>"
                    
                    send_msg(msg)
                    history.append(unique_id)
                    new_jobs_found = True
        except Exception as e:
            print(f"Error in {dist}: {e}")
            continue

    if new_jobs_found:
        with open(DB_FILE, "w") as f:
            # सिर्फ लेटेस्ट 100 रिकॉर्ड्स रखें ताकि फाइल भारी न हो
            json.dump(history[-100:], f)

if __name__ == "__main__":
    check_updates()
