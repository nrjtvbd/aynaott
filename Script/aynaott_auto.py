import requests
import json
import re
from datetime import datetime

def get_live_token():
    # সরাসরি সাইট থেকে টোকেন নেয়ার চেষ্টা
    url = "https://aynaott.com/live/btv-world"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Referer": "https://aynaott.com/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        match = re.search(r'index\.m3u8\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', response.text)
        if match:
            return match.group(1)
    except:
        pass
    return None

def main():
    print("🚀 Syncing All Channels with Global Token...")
    
    token_query = get_live_token()
    
    # টোকেন কাজ না করলে আপনার দেওয়া লেটেস্ট টোকেনটি এখানে থাকবে
    if not token_query:
        token_query = "e=1775940669&u=78be6644-0a65-48ec-81a4-089ac65a2619&token=195bd93f51092339fd1d166017efd6b3"

    # এখানে আইডিগুলো আপডেট করা হয়েছে আয়নাস্কোপের সার্ভার অনুযায়ী
    channels = [
        {"name": "BTV World", "id": "btv_world", "srv": "tvsen6"},
        {"name": "Somoy TV", "id": "somoy_tv", "srv": "tvsen6"},
        {"name": "T Sports", "id": "t_sports_hd", "srv": "tvsen7"},
        {"name": "GTV Live", "id": "gtv_live", "srv": "tvsen6"},
        {"name": "Jamuna TV", "id": "jamuna_tv", "srv": "tvsen6"},
        {"name": "Independent TV", "id": "independent_tv", "srv": "tvsen6"}
    ]
    
    m3u_content = "#EXTM3U\n"
    for ch in channels:
        # ক্লিন ইউআরএল তৈরি
        final_url = f"https://{ch['srv']}.aynascope.net/{ch['id']}/index.m3u8?{token_query}"
        m3u_content += f'#EXTINF:-1 group-title="AynaOTT",{ch["name"]}\n{final_url}\n\n'

    with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    with open("internal_data.json", "w", encoding="utf-8") as f:
        json.dump({"updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "token": token_query}, f, indent=4)

    print(f"✅ All channels linked with token: {token_query[:20]}...")

if __name__ == "__main__":
    main()
