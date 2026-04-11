import requests
import re
import os
from datetime import datetime

# সেশন এবং হেডার সেটআপ (ব্রাউজারকে নকল করার জন্য)
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Referer": "https://aynaott.com/"
}

def get_token_via_proxy(channel_id):
    """মনিরুলের লিঙ্ক থেকে প্রক্সির মাধ্যমে অরিজিনাল টোকেন বের করার চেষ্টা"""
    # সরাসরি রিকোয়েস্ট ব্লক হলে আমরা AllOrigins প্রক্সি ব্যবহার করব
    target_url = f"http://sm-monirul.top/AyNa/play.php?id={channel_id}"
    proxy_url = f"https://api.allorigins.win/get?url={target_url}"
    
    try:
        response = requests.get(proxy_url, timeout=15)
        if response.status_code == 200:
            content = response.json().get('contents', '')
            # আয়নাস্কোপের টোকেন প্যাটার্ন খোঁজা
            match = re.search(r'\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', content)
            if match:
                return match.group(1)
    except:
        pass
    return None

def main():
    print("🚀 Starting Advanced 272+ Channel Auto-Inspector...")
    
    source_file = "Script/aynaott.txt"
    if not os.path.exists(source_file):
        print("❌ Error: aynaott.txt not found!")
        return

    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()

    # আপনার ফাইলের ফরম্যাট অনুযায়ী আইডি এবং নাম খুঁজে বের করা
    # ফরম্যাট: play.php?id=XXXXX
    matches = re.findall(r'#EXTINF:.*,(.*)\n.*id=([^&\s]+)', content)

    if not matches:
        print("❌ No channels detected! Please check the txt file format.")
        return

    print(f"📂 Found {len(matches)} channels. Syncing now...")

    m3u_content = "#EXTM3U\n"
    success_count = 0
    # আপনার সবশেষ কাজ করা লেটেস্ট টোকেনটি এখানে ব্যাকআপ হিসেবে থাকবে
    fallback_token = "e=1775943478&u=78be6644-0a65-48ec-81a4-089ac65a2619&token=ad943974b438c7507cfb7d505f02b373"

    for i, (name, ch_id) in enumerate(matches, 1):
        name = name.strip()
        ch_id = ch_id.strip()
        
        # স্পোর্টস বা নির্দিষ্ট কিছু চ্যানেলের জন্য সার্ভার নির্বাচন
        srv = "tvsen7" if "tsport" in ch_id.lower() or "sports" in ch_id.lower() else "tvsen6"
        
        print(f"🔍 [{i}/{len(matches)}] Inspecting: {name}...")
        
        # প্রক্সি মেথডে টোকেন খোঁজা
        token = get_token_via_proxy(ch_id)
        
        if token:
            print(f"   ✅ Fresh Token Hijacked!")
            success_count += 1
        else:
            # যদি প্রক্সি ফেইল করে, তবে আমরা আমাদের হাতে থাকা লেটেস্ট টোকেনটি বসাবো
            token = fallback_token
            print(f"   ⚠️ Fallback applied.")

        # ফাইনাল অরিজিনাল আয়নাস্কোপ লিঙ্ক
        final_url = f"https://{srv}.aynascope.net/{ch_id}/index.m3u8?{token}"
        m3u_content += f'#EXTINF:-1 group-title="AynaOTT", {name}\n{final_url}\n\n'

    # ফাইল সেভ করা
    with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"\n✨ Task Finished! Total: {len(matches)} | Success: {success_count}")

if __name__ == "__main__":
    main()
