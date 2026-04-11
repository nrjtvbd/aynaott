import requests
import re
import os
from datetime import datetime

# সেশন এবং হেডার সেটআপ
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Referer": "https://aynaott.com/"
}

def inspect_token(php_url):
    """মনিরুলের পিএইচপি লিঙ্ক থেকে আসল টোকেন উদ্ধার করা"""
    try:
        res = session.get(php_url, headers=headers, timeout=12, allow_redirects=True)
        # ইউআরএল বা রেসপন্স বডি থেকে টোকেন প্যারামিটার খোঁজা
        match = re.search(r'\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', res.url)
        if not match:
            match = re.search(r'\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', res.text)
        return match.group(1) if match else None
    except:
        return None

def main():
    print("🚀 Starting Fully Automated Channel Discovery & Inspection...")
    
    # আপনার আপলোড করা aynaott.txt ফাইলটি রিড করা
    source_file = "Script/aynaott.txt"
    if not os.path.exists(source_file):
        print(f"❌ Error: {source_file} নথিপত্রটি খুঁজে পাওয়া যায়নি!")
        return

    with open(source_file, "r", encoding="utf-8") as f:
        raw_data = f.read()

    # রেজেক্স দিয়ে চ্যানেলের নাম এবং আইডি (PHP লিঙ্ক থেকে) অটোমেটিক খুঁজে বের করা
    # এটি মনিরুলের ফাইলের সব চ্যানেল (৯০-২০০+) ক্যাপচার করবে
    pattern = r'#EXTINF:.*,(.*)\nhttp://sm-monirul\.top/Ayha/play\.php\?id=(.*)'
    matches = re.findall(pattern, raw_data)

    if not matches:
        print("⚠️ কোনো চ্যানেল খুঁজে পাওয়া যায়নি! ফাইলের ফরম্যাট চেক করুন।")
        return

    print(f"📂 Found {len(matches)} channels in source file. Starting inspection...")

    m3u_content = "#EXTM3U\n"
    success_count = 0
    fallback = "e=1775943478&u=78be6644-0a65-48ec-81a4-089ac65a2619&token=ad943974b438c7507cfb7d505f02b373"

    for name, channel_id in matches:
        name = name.strip()
        channel_id = channel_id.strip()
        
        # সার্ভার ডিটেকশন (T Sports সাধারণত tvsen7 এ থাকে, বাকিরা tvsen6)
        srv = "tvsen7" if "tsports" in channel_id.lower() else "tvsen6"
        
        print(f"🔍 Inspecting: {name} ({channel_id})...")
        php_link = f"http://sm-monirul.top/Ayha/play.php?id={channel_id}"
        token = inspect_token(php_link)
        
        if token:
            print(f"✅ Fresh Token Found!")
            success_count += 1
        else:
            print(f"⚠️ Inspection failed, using fallback.")
            token = fallback

        # অরিজিনাল আয়নাস্কোপ লিঙ্ক জেনারেশন
        final_url = f"https://{srv}.aynascope.net/{channel_id}/index.m3u8?{token}"
        m3u_content += f'#EXTINF:-1 group-title="AynaOTT", {name}\n{final_url}\n\n'

    # আউটপুট ফাইল সেভ করা
    with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"\n✨ Done! Successfully processed {len(matches)} channels.")
    print(f"📈 Fresh Tokens: {success_count} | Fallbacks used: {len(matches) - success_count}")

if __name__ == "__main__":
    main()
