import requests
import re
import json
from datetime import datetime

def fetch_btv_world():
    # সেশন ব্যবহার করলে কুকি এবং কানেকশন বজায় থাকে, যা ডিটেকশন এড়াতে সাহায্য করে
    session = requests.Session()
    
    page_url = "https://aynaott.com/live/btv-world" 
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
        "Referer": "https://aynaott.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1"
    }

    try:
        # প্রথমে হোমপেজে গিয়ে কুকি সেট করা (বট ডিটেকশন এড়াতে)
        session.get("https://aynaott.com/", headers=headers, timeout=15)
        
        # এবার সরাসরি চ্যানেলের পেজ রিকোয়েস্ট করা
        print(f"📡 Fetching BTV World with Session...")
        response = session.get(page_url, headers=headers, timeout=20)
        source = response.text

        # আপনার দেওয়া লিঙ্ক স্ট্রাকচার অনুযায়ী রেজেক্স
        # e, u এবং token খুঁজে বের করা
        link_match = re.search(r'https?://tvsen6\.aynascope\.net/btv_world/index\.m3u8\?e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+', source)
        
        if link_match:
            print(f"✅ Link Found: {link_match.group(0)[:50]}...")
            return link_match.group(0)
        
        # যদি ফুল লিঙ্ক না পাওয়া যায়, তবে ভেঙে ভেঙে খোঁজা
        token = re.search(r'token=([a-zA-Z0-9]+)', source)
        if token:
            expiry = re.search(r'e=(\d+)', source).group(1)
            uid = re.search(r'u=([a-z0-9-]+)', source).group(1)
            final_url = f"https://tvsen6.aynascope.net/btv_world/index.m3u8?e={expiry}&u={uid}&token={token.group(1)}"
            return final_url

    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    return None

def main():
    live_link = fetch_btv_world()
    
    if live_link:
        vlc_headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36&Referer=https://aynaott.com/"
        
        data = {
            "status": "active",
            "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "payload": [{"name": "BTV World", "src": live_link}]
        }
        
        m3u = f'#EXTM3U\n#EXTINF:-1 group-title="AynaOTT",BTV World\n{live_link}{vlc_headers}'
        
        with open("internal_data.json", "w", encoding="utf-8") as jf:
            json.dump(data, jf, indent=4)
        with open("AynaOTT.m3u", "w", encoding="utf-8") as mf:
            mf.write(m3u)
        print("🚀 Success! Files updated.")
    else:
        print("❌ Still failing. Aynascope is blocking GitHub Runners.")

if __name__ == "__main__":
    main()
