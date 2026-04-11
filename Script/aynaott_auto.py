import requests
import json
import re
from datetime import datetime

# সেশন এবং হেডার সেটআপ (মোবাইল অ্যাপ স্টাইল)
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Referer": "https://aynaott.com/",
    "X-Requested-With": "com.ayna.ott"
}

def get_token(slug):
    """প্রতিটি চ্যানেলের জন্য আলাদা টোকেন সংগ্রহের ফাংশন"""
    url = f"https://aynaott.com/live/{slug}"
    try:
        response = session.get(url, headers=headers, timeout=15)
        source = response.text
        # রেজেক্স দিয়ে e, u, token প্যারামিটারগুলো খুঁজে বের করা
        match = re.search(r'index\.m3u8\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', source)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"❌ Error fetching {slug}: {e}")
    return None

def main():
    print("🚀 Running RoarZone Style Multi-Token Scraper...")
    
    # চ্যানেলের তালিকা (ওয়েব স্লাগ এবং সার্ভার আইডি আলাদা করা হয়েছে)
    channels = [
        {"name": "BTV World", "web_slug": "btv-world", "srv_id": "btv_world", "srv": "tvsen6"},
        {"name": "T Sports HD", "web_slug": "t-sports-hd", "srv_id": "tsports-hd", "srv": "tvsen7"},
        {"name": "Somoy TV", "web_slug": "somoy-tv", "srv_id": "somoy_tv", "srv": "tvsen6"},
        {"name": "GTV Live", "web_slug": "gtv-live", "srv_id": "gtv_live", "srv": "tvsen6"},
        {"name": "Jamuna TV", "web_slug": "jamuna-tv", "srv_id": "jamuna_tv", "srv": "tvsen6"}
    ]
    
    # ফলব্যাক টোকেন (যদি গিটহাব আইপি ব্লক থাকে তবে এটি ব্যবহার হবে)
    fallback_token = "e=1775943478&u=78be6644-0a65-48ec-81a4-089ac65a2619&token=ad943974b438c7507cfb7d505f02b373"

    m3u_content = "#EXTM3U\n"
    
    for ch in channels:
        print(f"📡 Syncing: {ch['name']}...")
        token = get_token(ch['web_slug'])
        
        if not token:
            print(f"⚠️ IP Blocked for {ch['name']}, using fallback.")
            token = fallback_token
        
        # ক্লিন ইউআরএল জেনারেশন
        final_url = f"https://{ch['srv']}.aynascope.net/{ch['srv_id']}/index.m3u8?{token}"
        m3u_content += f'#EXTINF:-1 group-title="AynaOTT" tvg-id="{ch["srv_id"]}", {ch["name"]}\n{final_url}\n\n'

    # ফাইল সেভ করা
    with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"\n✅ All Done! Playlist generated at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
