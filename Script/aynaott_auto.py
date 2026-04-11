import requests
import json
import re
import os
from datetime import datetime

def get_live_token():
    """আয়নাস্কোপ থেকে টোকেন সংগ্রহের চেষ্টা"""
    url = "https://aynaott.com/live/btv-world"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Referer": "https://aynaott.com/"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        source = response.text
        
        # লিঙ্ক থেকে প্যারামিটার বের করা (e, u, token)
        match = re.search(r'index\.m3u8\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', source)
        if match:
            return match.group(1)
    except:
        pass
    return None

def main():
    print("🚀 Generating Clean Playlist (No User-Agent in Link)...")
    
    token_query = get_live_token()
    
    # যদি গিটহাব ব্লক থাকে, তবে আপনার দেওয়া লেটেস্ট টোকেনটি এখানে থাকবে
    if not token_query:
        print("⚠️ GitHub IP Blocked. Using manual token fallback.")
        # আপনি এখানে আপনার ব্রাউজার থেকে পাওয়া লেটেস্ট কোয়েরিটি বসিয়ে দিতে পারেন
        token_query = "e=1775940669&u=78be6644-0a65-48ec-81a4-089ac65a2619&token=195bd93f51092339fd1d166017efd6b3"

    channels = [
        {"name": "BTV World", "id": "btv_world", "srv": "tvsen6"},
        {"name": "T Sports", "id": "t_sports_hd", "srv": "tvsen7"},
        {"name": "Somoy TV", "id": "somoy_tv", "srv": "tvsen6"},
        {"name": "GTV Live", "id": "gtv_live", "srv": "tvsen6"}
    ]
    
    m3u_content = "#EXTM3U\n"
    payload = []

    for ch in channels:
        # একদম ক্লিন লিঙ্ক জেনারেশন
        final_url = f"https://{ch['srv']}.aynascope.net/{ch['id']}/index.m3u8?{token_query}"
        
        m3u_content += f'#EXTINF:-1 group-title="AynaOTT",{ch["name"]}\n{final_url}\n\n'
        payload.append({"name": ch["name"], "url": final_url})
        print(f"✅ Added: {ch['name']}")

    # ফাইল সেভ করা
    with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    with open("internal_data.json", "w", encoding="utf-8") as f:
        json.dump({
            "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "token_used": token_query,
            "channels": payload
        }, f, indent=4)

    print("✨ Clean playlist generated successfully.")

if __name__ == "__main__":
    main()
