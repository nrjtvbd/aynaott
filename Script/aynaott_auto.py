import requests
import re
import os
import concurrent.futures
from datetime import datetime

# সেশন এবং হেডার সেটআপ
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Referer": "https://aynaott.com/",
    "Origin": "https://aynaott.com"
}

def fetch_individual_token(ch_name, ch_id):
    """প্রতিটি চ্যানেলের জন্য আলাদা টোকেন সংগ্রহ করার ফাংশন"""
    # সরাসরি ব্লক এড়াতে AllOrigins প্রক্সি ব্যবহার
    target_url = f"http://sm-monirul.top/AyNa/play.php?id={ch_id}"
    proxy_url = f"https://api.allorigins.win/get?url={target_url}"
    
    try:
        response = session.get(proxy_url, timeout=15)
        if response.status_code == 200:
            content = response.json().get('contents', '')
            # আয়নাস্কোপের ইউনিক টোকেন প্যাটার্ন খোঁজা
            match = re.search(r'\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', content)
            if match:
                token = match.group(1)
                srv = "tvsen7" if "tsport" in ch_id.lower() or "sports" in ch_id.lower() else "tvsen6"
                final_link = f"https://{srv}.aynascope.net/{ch_id}/index.m3u8?{token}"
                return f'#EXTINF:-1 group-title="NRJTVBD", {ch_name}\n{final_link}\n\n'
    except:
        pass
    return None

def main():
    print(f"🚀 Starting Multi-Threaded Inspection for 272 Channels...")
    start_time = datetime.now()

    source_file = "Script/aynaott.txt"
    if not os.path.exists(source_file):
        print("❌ Error: aynaott.txt not found!")
        return

    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()

    # নাম এবং আইডি খুঁজে বের করা
    matches = re.findall(r'#EXTINF:.*,(.*)\n.*id=([^&\s]+)', content)
    
    if not matches:
        print("❌ No channels found in source.")
        return

    print(f"📂 Found {len(matches)} channels. Scanning tokens independently...")

    m3u_content = "#EXTM3U\n"
    results = []

    # ২৭২টি চ্যানেল একে একে করলে অনেক সময় লাগবে, তাই থ্রেডিং ব্যবহার করছি যাতে দ্রুত হয়
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ch = {executor.submit(fetch_individual_token, name.strip(), ch_id.strip()): name for name, ch_id in matches}
        for future in concurrent.futures.as_completed(future_to_ch):
            res = future.result()
            if res:
                results.append(res)
                print(f"✅ Extracted: {future_to_ch[future]}")
            else:
                print(f"❌ Failed: {future_to_ch[future]}")

    # প্লেলিস্ট তৈরি
    for entry in results:
        m3u_content += entry

    with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\n✨ Task Finished in {duration.seconds}s!")
    print(f"📊 Successfully Synced: {len(results)}/{len(matches)} channels.")

if __name__ == "__main__":
    main()
