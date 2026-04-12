import requests
import re
import os
import time
import random
from concurrent.futures import ThreadPoolExecutor

# ব্রাউজারের মতো নিখুঁত হেডার
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"
]

def hijack_token_v2(name, ch_id):
    """মনিরুলের PHP ফাইল রেন্ডার করে টোকেন বের করার শেষ চেষ্টা"""
    url = f"http://sm-monirul.top/AyNa/play.php?id={ch_id}"
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://aynaott.com/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        # কোনো প্রক্সি ছাড়া সরাসরি রিকোয়েস্ট
        response = requests.get(url, headers=headers, timeout=12)
        
        if response.status_code == 200:
            html = response.text
            # টোকেনের রেগুলার এক্সপ্রেশন (প্যাটার্ন ১)
            token_match = re.search(r'\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', html)
            
            if not token_match:
                # যদি সরাসরি না পাওয়া যায়, তবে রিডাইরেক্ট ইউআরএল চেক করা
                token_match = re.search(r'index\.m3u8\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', html)

            if token_match:
                token = token_match.group(1)
                
                # সার্ভার নোড নির্ধারণ
                if "tsports" in ch_id.lower() or "sports" in ch_id.lower():
                    srv = "tvsen7"
                elif "star" in ch_id.lower() or len(ch_id) > 20:
                    srv = "tvsen5"
                else:
                    srv = "tvsen6"
                
                final_link = f"https://{srv}.aynascope.net/{ch_id}/index.m3u8?{token}"
                return f'#EXTINF:-1 group-title="NRJTVBD", {name}\n{final_link}\n\n'
    except:
        pass
    return None

def main():
    print("🧨 Initiating Ultimate Token Hijacker...")
    source_file = "Script/aynaott.txt"
    
    if not os.path.exists(source_file):
        print("❌ aynaott.txt missing!")
        return

    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()

    matches = re.findall(r'#EXTINF:.*,(.*)\n.*id=([^&\s]+)', content)
    print(f"🎯 Targeted Channels: {len(matches)}")

    results = []
    # ৩টি থ্রেড দিয়ে ধীরগতিতে কাজ করা (যাতে ব্লক না করে)
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(hijack_token_v2, n.strip(), i.strip()): n for n, i in matches}
        
        for future in futures:
            res = future.result()
            if res:
                results.append(res)
                print(f"✅ {futures[future]} -> Token Captured!")
            else:
                print(f"💀 {futures[future]} -> Access Denied")
            
            # সার্ভারকে সন্দেহ করার সুযোগ না দিতে র্যান্ডম গ্যাপ
            time.sleep(random.uniform(0.5, 1.5))

    with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n" + "".join(results))

    print(f"\n✨ Extraction Completed. Total: {len(results)} channels.")

if __name__ == "__main__":
    main()
