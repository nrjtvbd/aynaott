import requests
import json
from datetime import datetime

def main():
    print("🚀 Running AynaOTT Mirror Scraper (Fixed Source)...")

    # মনিরুল ইসলামের রিপোজিটরির বর্তমান সঠিক ডাটা সোর্স
    # এই লিঙ্কগুলো গিটহাবের ভেতরে থাকায় ব্লক হওয়ার ভয় নেই
    url = "https://raw.githubusercontent.com/m-m-i-n/AynaOTT/main/assets/data.json"

    try:
        print(f"📡 Fetching mirroring data...")
        response = requests.get(url, timeout=20)
        
        if response.status_code != 200:
            print(f"❌ Source failed with status: {response.status_code}")
            return

        data_json = response.json()
        
        # ডাটা থেকে চ্যানেলের লিস্ট বের করা
        # তারা যদি সরাসরি লিস্ট দেয় অথবা 'payload' কি-এর ভেতরে দেয়
        channels = data_json if isinstance(data_json, list) else data_json.get("payload", []) or data_json.get("channels", [])

        if not channels:
            print("⚠️ No channel data found in source JSON.")
            return

        vlc_headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36&Referer=https://aynaott.com/"

        # M3U এবং JSON ফাইল তৈরি
        m3u_content = "#EXTM3U\n"
        for ch in channels:
            name = ch.get("name") or ch.get("title", "Unknown")
            src = ch.get("src") or ch.get("url", "").strip()
            logo = ch.get("logo", "")
            
            if src:
                m3u_content += f'#EXTINF:-1 tvg-logo="{logo}" group-title="AynaOTT",{name}\n'
                m3u_content += f"{src}{vlc_headers}\n\n"

        with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
            f.write(m3u_content)
        
        with open("internal_data.json", "w", encoding="utf-8") as f:
            json.dump({"last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "payload": channels}, f, indent=4)

        print(f"✅ Success! Updated with {len(channels)} channels.")

    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    main()
