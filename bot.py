import requests
from bs4 import BeautifulSoup
import os

# GitHub Secrets से डेटा लेना
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# झारखंड के सभी 24 जिले
DISTRICTS = [
    "ranchi", "dhanbad", "bokaro", "jamshedpur", "deoghar", "hazaribag", "giridih", "dumka",
    "godda", "sahibganj", "palamu", "garhwa", "latehar", "chatra", "kodiarm", "gumla", 
    "lohardaga", "simdega", "khunti", "ramgarh", "pakur", "jamtara", "west-singhbhum", "seraiekela"
]

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.get(url, params={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

def check_jobs():
    for dist in DISTRICTS:
        url = f"https://{dist}.nic.in/notice/recruitment/"
        try:
            r = requests.get(url, timeout=20)
            soup = BeautifulSoup(r.text, 'html.parser')
            table = soup.find('table')
            if table:
                row = table.find_all('tr')[1]
                title = row.find_all('td')[0].text.strip()
                date = row.find_all('td')[2].text.strip() # End Date
                
                # सिर्फ आज या हाल के नोटिस के लिए (Option: Aap isse filter kar sakte hain)
                msg = f"<b>📍 District: {dist.upper()}</b>\n📝 Job: {title}\n📅 Last Date: {date}\n🔗 <a href='{url}'>Click here to Apply</a>"
                send_msg(msg)
        except:
            continue

# High Court Check
def check_hc():
    url = "https://jharkhandhighcourt.nic.in/recruitment"
    try:
        r = requests.get(url)
        if "Recruitment" in r.text:
            send_msg(f"<b>⚖️ Jharkhand High Court</b>\nNaya notification check karein.\n🔗 {url}")
    except:
        pass

if __name__ == "__main__":
    check_jobs()
    check_hc()
