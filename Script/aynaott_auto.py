import requests
import re
from datetime import datetime

def sync_from_monirul():
    """মনিরুল ইসলামের সচল প্লেলিস্ট থেকে টোকেন 'হাইজ্যাক' করার মেথড"""
    url = "https://raw.githubusercontent.com/sm-monirulislam/SM-Live-TV/refs/heads/main/AynaOTT.m3u"
    try:
        print(f"📡 Syncing from Monirul's Mirror...")
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            content = response.text
            # প্লেলিস্ট থেকে লেটেস্ট টোকেন কুয়েরি খুঁজে বের করা
            match = re.search(r'\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', content)
            if match:
                return match.group(1)
    except:
        pass
    return None

def main():
    print("🚀 Starting Hybrid AynaOTT Update...")
    
    # প্রথমে মনিরুল ইসলামের ফাইল থেকে টোকেন নেয়ার চেষ্টা
    fresh_token = sync_from_monirul()
    
    if fresh_token:
        print("✅ Fresh token hijacked from Monirul!")
    else:
        print("⚠️ Mirror sync failed. Using static fallback.")
        # আপনার সবশেষ কাজ করা টোকেনটি এখানে থাকবে
        fresh_token = "e=1775943478&u=78be6644-0a65-48ec-81a4-089ac65a2619&token=ad943974b438c7507cfb7d505f02b373"

    # চ্যানেলের তালিকা
    channels = [
        {"name": "BTV World", "id": "btv_world", "srv": "tvsen6"},
        {"name": "T Sports HD", "id": "tsports-hd", "srv": "tvsen7"},
        {"name": "Somoy TV", "id": "somoy_tv", "srv": "tvsen6"},
        {"name": "GTV Live", "id": "gtv_live", "srv": "tvsen6"}
    ]

    m3u_content = "#EXTM3U\n"
    for ch in channels:
        final_url = f"https://{ch['srv']}.aynascope.net/{ch['id']}/index.m3u8?{fresh_token}"
        m3u_content += f'#EXTINF:-1 group-title="AynaOTT", {ch["name"]}\n{final_url}\n\n'

    with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"✨ Update Complete using token: {fresh_token[:15]}...")

if __name__ == "__main__":
    main()
