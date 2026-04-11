import requests
import re
import json
from datetime import datetime

def get_token_stealth(slug):
    session = requests.Session()
    
    # এটি মনিরুল ইসলামের মতো ডেভেলপারদের গোপন অস্ত্র: নিখুঁত হেডার সেট
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://aynaott.com/",
        "Origin": "https://aynaott.com",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site"
    }

    try:
        # ধাপ ১: প্রথমে পেজটি লোড করা যাতে সেশন কুকি তৈরি হয়
        page_url = f"https://aynaott.com/live/{slug}"
        res = session.get(page_url, headers=headers, timeout=15)
        
        # ধাপ ২: সোর্স কোড থেকে টোকেন কোয়েরি খোঁজা
        # আয়নাস্কোপের ইন্টারনাল স্ক্রিপ্ট এখন এই ফরম্যাটে টোকেন জেনারেট করে
        source = res.text
        token_match = re.search(r'token=([a-zA-Z0-9]+)', source)
        expiry_match = re.search(r'e=(\d+)', source)
        uid_match = re.search(r'u=([a-z0-9-]+)', source)
        
        if token_match and expiry_match:
            e = expiry_match.group(1)
            token = token_match.group(1)
            u = uid_match.group(1)
            
            # সার্ভার অটো ডিটেকশন (tvsen6/tvsen7)
            server = "tvsen6" if "tvsen6" in source else "tvsen7"
            # স্লাগ কনভারশন (btv-world -> btv_world)
            clean_slug = slug.replace('-', '_')
            
            final_url = f"https://{server}.aynascope.net/{clean_slug}/index.m3u8?e={e}&u={u}&token={token}"
            return final_url
    except:
        pass
    return None

def main():
    channels = [
        {"name": "BTV World", "slug": "btv-world"},
        {"name": "T Sports HD", "slug": "t-sports-hd"},
        {"name": "Somoy TV", "slug": "somoy-tv"},
        {"name": "GTV Live", "slug": "gtv-live"}
    ]
    
    print("🚀 Running Stealth Scraper (AynaOTT Method)...")
    
    internal_data = {"status": "active", "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "payload": []}
    m3u_content = "#EXTM3U\n"
    vlc_headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36&Referer=https://aynaott.com/"

    success = 0
    for ch in channels:
        url = get_token_stealth(ch['slug'])
        if url:
            internal_data["payload"].append({"name": ch['name'], "src": url})
            m3u_content += f'#EXTINF:-1 group-title="AynaOTT",{ch["name"]}\n{url}{vlc_headers}\n\n'
            print(f"✅ {ch['name']} updated.")
            success += 1
        else:
            print(f"❌ {ch['name']} failed.")

    if success > 0:
        with open("internal_data.json", "w") as f: json.dump(internal_data, f, indent=4)
        with open("AynaOTT.m3u", "w") as f: f.write(m3u_content)
        print(f"\n✨ Done! {success} channels ready.")

if __name__ == "__main__":
    main()
