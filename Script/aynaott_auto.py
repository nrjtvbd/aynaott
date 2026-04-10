import requests
import re
import json
import os
from datetime import datetime

def get_all_channels():
    """আয়নাস্কোপের হোমপেজ থেকে সব চ্যানেলের স্লাগ এবং নাম সংগ্রহ করার ফাংশন"""
    url = "https://aynascope.net/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
    }
    
    try:
        print("🔎 Scanning AynaOTT for all available channels...")
        response = requests.get(url, headers=headers, timeout=15)
        # HTML থেকে চ্যানেলের স্লাগ এবং টাইটেল বের করার প্যাটার্ন
        # সাধারণত /live/slug ফরম্যাটে থাকে
        matches = re.findall(r'href="https://aynascope\.net/live/([a-zA-Z0-9_-]+)".*?title="(.*?)"', response.text)
        
        channels = []
        unique_slugs = set()
        
        for slug, title in matches:
            if slug not in unique_slugs:
                channels.append({"name": title, "slug": slug})
                unique_slugs.add(slug)
        
        print(f"✅ Found {len(channels)} channels automatically.")
        return channels
    except Exception as e:
        print(f"❌ Could not scrape channel list: {e}")
        return []

def fetch_ayna_info(slug):
    """প্রতিটি চ্যানেলের জন্য লেটেস্ট টোকেন এবং সার্ভার ইউআরএল খুঁজে বের করা"""
    base_url = f"https://aynascope.net/live/{slug}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Referer": "https://aynascope.net/"
    }
    
    try:
        response = requests.get(base_url, headers=headers, timeout=15)
        source = response.text
        
        # সার্ভার এবং ইনডেক্স ফাইল প্যাটার্ন (tvsen5/7 হ্যান্ডলিং)
        stream_match = re.search(r'(https?://[a-z0-9.]+/([a-zA-Z0-9_-]+)/)index\.m3u8', source)
        if not stream_match: return None
        
        main_stream_url = stream_match.group(1) + "index.m3u8"
        
        # টোকেন এবং প্যারামিটার এক্সট্রাকশন
        token = re.search(r'token=([a-zA-Z0-9]+)', source).group(1)
        expiry = re.search(r'e=(\d+)', source).group(1)
        uid = re.search(r'u=([a-z0-9-]+)', source).group(1)
        
        return f"{main_stream_url}?e={expiry}&u={uid}&token={token}"
    except:
        return None

def main():
    # ম্যানুয়ালি লিস্ট দেওয়ার বদলে এখন অটোমেটিক সংগ্রহ হবে
    channels_to_track = get_all_channels()
    
    if not channels_to_track:
        print("❌ No channels found. Exiting.")
        return

    vlc_headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36&Referer=https://aynascope.net/"
    
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
            # Roarzone স্টাইল JSON পেলোড তৈরি
            internal_data["payload"].append({
                "name": ch['name'],
                "src": live_link,
                "type": "LiveTV"
            })
            
            # M3U ফরম্যাট জেনারেশন
            m3u_content += f'#EXTINF:-1 group-title="AynaOTT",{ch["name"]}\n'
            m3u_content += f"{live_link}{vlc_headers}\n\n"
            print(f"✔️ Added: {ch['name']}")

    # ফাইলগুলো সেভ করা
    with open("internal_data.json", "w", encoding="utf-8") as jf:
        json.dump(internal_data, jf, indent=4)
        
    with open("AynaOTT.m3u", "w", encoding="utf-8") as mf:
        mf.write(m3u_content)

if __name__ == "__main__":
    main()
