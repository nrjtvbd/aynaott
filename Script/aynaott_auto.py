import requests
import re
import json
from datetime import datetime

# ==========================================================
# ১. সব চ্যানেলের লিস্ট সংগ্রহ করার ফাংশন
# ==========================================================
def get_all_channels():
    """aynaott.com থেকে সব চ্যানেলের নাম এবং স্লাগ সংগ্রহ করার উন্নত ফাংশন"""
    url = "https://aynaott.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print(f"🔎 Scanning {url} for all available channels...")
        response = requests.get(url, headers=headers, timeout=15)
        
        # জেনারেল প্যাটার্ন যা /live/ স্লাগ এবং চ্যানেলের নাম খুঁজে বের করবে
        matches = re.findall(r'href=["\'](?:https://aynaott\.com)?/live/([a-zA-Z0-9_-]+)["\'].*?>(.*?)<', response.text)
        
        channels = []
        unique_slugs = set()
        
        for slug, title in matches:
            # HTML ট্যাগ পরিষ্কার করা এবং নাম ঠিক করা
            clean_name = re.sub('<[^<]+?>', '', title).strip()
            if not clean_name: clean_name = slug.replace('-', ' ').title()
            
            if slug not in unique_slugs:
                channels.append({"name": clean_name, "slug": slug})
                unique_slugs.add(slug)
        
        # যদি অটোমেটিক কিছুই না পায়, তবে ব্যাকআপ হিসেবে প্রধান চ্যানেলগুলো থাকবে
        if not channels:
            print("⚠️ Automatic scan failed, using fallback list.")
            channels = [
                {"name": "Somoy TV", "slug": "somoy-tv"},
                {"name": "T Sports", "slug": "t-sports"},
                {"name": "Jamuna TV", "slug": "jamuna-tv"},
                {"name": "Ekattor TV", "slug": "ekattor-tv"}
            ]
        
        print(f"✅ Found {len(channels)} channels.")
        return channels
    except Exception as e:
        print(f"❌ Could not scrape channel list: {e}")
        return []

# ==========================================================
# ২. প্রতিটি চ্যানেলের জন্য লাইভ লিঙ্ক এবং টোকেন সংগ্রহের ফাংশন
# ==========================================================
def fetch_ayna_info(slug):
    """সঠিক সার্ভার (tvsen5/7) এবং টোকেন খুঁজে বের করা"""
    base_url = f"https://aynaott.com/live/{slug}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://aynaott.com/"
    }
    
    try:
        response = requests.get(base_url, headers=headers, timeout=15)
        source = response.text
        
        # সার্ভার ইউআরএল প্যাটার্ন খুঁজে বের করা (যেমন tvsen7.aynascope.net/tsports-hd/index.m3u8)
        stream_match = re.search(r'(https?://[a-z0-9.]+\.aynascope\.net/([a-zA-Z0-9_-]+)/)index\.m3u8', source)
        if not stream_match: return None
        
        main_stream_url = stream_match.group(1) + "index.m3u8"
        
        # টোকেন, এক্সপায়ারি এবং ইউআইডি এক্সট্রাকশন
        token = re.search(r'token=([a-zA-Z0-9]+)', source).group(1)
        expiry = re.search(r'e=(\d+)', source).group(1)
        uid = re.search(r'u=([a-z0-9-]+)', source).group(1)
        
        return f"{main_stream_url}?e={expiry}&u={uid}&token={token}"
    except:
        return None

# ==========================================================
# ৩. মেইন ফাংশন (ফাইল জেনারেশন)
# ==========================================================
def main():
    print("🚀 Starting AynaOTT Auto Update...")
    
    channels_to_track = get_all_channels()
    
    # VLC-র জন্য প্রয়োজনীয় হেডার স্ট্রিং
    vlc_headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36&Referer=https://aynaott.com/"
    
    # Roarzone স্টাইল JSON স্ট্রাকচার
    internal_data = {
        "status": "active",
        "updated": True,
        "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "payload": []
    }
    
    m3u_content = "#EXTM3U\n"

    for ch in channels_to_track:
        live_link = fetch_ayna_info(ch['slug'])
        if live_link:
            # JSON-এ ডাটা যোগ করা
            internal_data["payload"].append({
                "name": ch['name'],
                "src": live_link,
                "type": "LiveTV"
            })
            
            # M3U ফাইলে ডাটা যোগ করা (VLC-র জন্য হেডারসহ)
            m3u_content += f'#EXTINF:-1 group-title="AynaOTT",{ch["name"]}\n'
            m3u_content += f"{live_link}{vlc_headers}\n\n"
            print(f"✔️ Added: {ch['name']}")

    # ১. internal_data.json ফাইল সেভ করা
    with open("internal_data.json", "w", encoding="utf-8") as jf:
        json.dump(internal_data, jf, indent=4)
    
    # ২. AynaOTT.m3u ফাইল সেভ করা
    with open("AynaOTT.m3u", "w", encoding="utf-8") as mf:
        mf.write(m3u_content)

    print("\n✅ Success! internal_data.json and AynaOTT.m3u have been updated.")

if __name__ == "__main__":
    main()
