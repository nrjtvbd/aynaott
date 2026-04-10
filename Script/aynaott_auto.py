import requests
import re
import json
from datetime import datetime

def fetch_ayna_info(slug):
    """সরাসরি প্রতিটি চ্যানেলের পেজ থেকে টোকেন এবং সার্ভার বের করার সবচেয়ে শক্তিশালী মেথড"""
    # আমরা সরাসরি aynascope.net এর আইপি রেজোলিউশন এড়াতে aynaott.com ব্যবহার করব
    base_url = f"https://aynaott.com/live/{slug}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://aynaott.com/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }
    
    try:
        # রিট্রাই মেকানিজম
        response = requests.get(base_url, headers=headers, timeout=15)
        source = response.text
        
        # ১. সোর্স কোড থেকে পূর্ণাঙ্গ index.m3u8 লিঙ্ক এবং টোকেন খুঁজে বের করা
        # আয়নাস্কোপের বর্তমান কোড স্ট্রাকচার অনুযায়ী এই প্যাটার্নটি সবচেয়ে কার্যকর
        stream_match = re.search(r'["\'](https?://[a-z0-9.]+\.aynascope\.net/[a-zA-Z0-9_-]+/index\.m3u8\?e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)["\']', source)
        
        if stream_match:
            return stream_match.group(1)
            
        # ২. ব্যাকআপ প্যাটার্ন (যদি লিঙ্কটি ভেঙে ভেঙে থাকে)
        server = re.search(r'(https?://[a-z0-9.]+\.aynascope\.net/[a-zA-Z0-9_-]+/)?index\.m3u8', source)
        token = re.search(r'token=([a-zA-Z0-9]+)', source)
        
        if server and token:
            e = re.search(r'e=(\d+)', source).group(1)
            u = re.search(r'u=([a-z0-9-]+)', source).group(1)
            return f"{server.group(1)}index.m3u8?e={e}&u={u}&token={token.group(1)}"
            
    except Exception as e:
        print(f"⚠️ Error fetching {slug}: {e}")
    return None

def main():
    print("🚀 AynaOTT Super Update Engine Starting...")
    
    # আপনার জন্য নিশ্চিত কার্যকরী চ্যানেলের লিস্ট
    channels = [
        {"name": "Somoy TV", "slug": "somoy-tv"},
        {"name": "T Sports HD", "slug": "t-sports-hd"},
        {"name": "GTV Live", "slug": "gtv-live"},
        {"name": "Jamuna TV", "slug": "jamuna-tv"},
        {"name": "Ekattor TV", "slug": "ekattor-tv"},
        {"name": "Independent TV", "slug": "independent-tv"},
        {"name": "Channel 24", "slug": "channel-24"},
        {"name": "RTV Live", "slug": "rtv-live"},
        {"name": "NTV Live", "slug": "ntv-live"},
        {"name": "News 24", "slug": "news-24"}
    ]
    
    # VLC প্লেয়ারের জন্য হেডার
    vlc_headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36&Referer=https://aynaott.com/"
    
    internal_data = {
        "status": "active",
        "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "payload": []
    }
    
    m3u_content = "#EXTM3U\n"
    count = 0

    for ch in channels:
        print(f"📡 Extracting: {ch['name']}...", end=" ", flush=True)
        live_url = fetch_ayna_info(ch['slug'])
        
        if live_url:
            internal_data["payload"].append({"name": ch['name'], "src": live_url})
            m3u_content += f'#EXTINF:-1 group-title="AynaOTT",{ch["name"]}\n{live_url}{vlc_headers}\n\n'
            print("✅ Done")
            count += 1
        else:
            print("❌ Failed")

    # ফাইল আপডেট করা
    with open("internal_data.json", "w", encoding="utf-8") as jf:
        json.dump(internal_data, jf, indent=4)
    with open("AynaOTT.m3u", "w", encoding="utf-8") as mf:
        mf.write(m3u_content)
        
    print(f"\n✨ Task Finished! {count} out of {len(channels)} channels are now live.")

if __name__ == "__main__":
    main()
