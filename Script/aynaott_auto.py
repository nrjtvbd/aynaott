import requests
import os
import json
from datetime import datetime

# ✅ API URL from GitHub Secret
API_URL = os.environ.get("AYNAOTT_API_URL")

def generate_playlist():
    print("🚀 Starting Auto Playlist Generator...")

    if not API_URL:
        print("❌ AYNAOTT_API_URL secret not found")
        return

    # আয়নাস্কোপের স্ট্রিমিং লিঙ্কগুলো সাধারণত এই হেডার ছাড়া কাজ করে না
    # তাই আমরা M3U ফাইলে এগুলো অ্যাপেন্ড করে দেব
    vlc_headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36&Referer=https://aynaott.com/"

    try:
        print("📡 Fetching data from API...")
        response = requests.get(API_URL, timeout=25)
        response.raise_for_status()
        raw = response.json()
    except Exception as e:
        print(f"❌ API Fetch Error: {e}")
        return

    # ডাটা ফরম্যাট হ্যান্ডলিং
    data = raw if isinstance(raw, list) else raw.get("response", [])

    if not isinstance(data, list) or len(data) == 0:
        print("⚠️ Valid channel data not found.")
        return

    file_path = "AynaOTT.m3u"
    json_path = "internal_data.json"

    try:
        # ১. M3U ফাইল জেনারেট করা
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            channel_count = 0

            for ch in data:
                if not isinstance(ch, dict): continue
                
                name = ch.get("title", "Unknown")
                logo = ch.get("logo", "")
                url = ch.get("url", "").strip()
                group = ch.get("category", "AynaOTT")

                if url:
                    # লিঙ্ক এর সাথে হেডার যোগ করা যাতে সব প্লেয়ারে চলে
                    f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{name}\n')
                    f.write(f"{url}{vlc_headers}\n\n")
                    channel_count += 1
            
            f.write(f"# Total Channels: {channel_count}\n")
            f.write(f"# Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # ২. ব্যাকআপের জন্য JSON ফাইল জেনারেট করা (আপনার অ্যাপের জন্য সুবিধা হবে)
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump({
                "status": "active",
                "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "channels": data
            }, jf, indent=4)

        print(f"✅ Success! Generated {channel_count} channels.")

    except Exception as e:
        print(f"❌ File Writing Error: {e}")

if __name__ == "__main__":
    generate_playlist()
