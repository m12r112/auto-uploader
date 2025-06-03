import os
import json
from pathlib import Path
from g4f.client import Client

OUTPUT_REELS_DIR = Path("output_reels")
CAPTIONS_OUTPUT_FILE = "captions.json"

# تأكد من وجود المجلد
OUTPUT_REELS_DIR.mkdir(exist_ok=True)

# تهيئة GPT4Free
client = Client()

def detect_category_from_folder_name(folder_name):
    return folder_name.lower()

def generate_caption(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a social media expert. Write viral, subconscious-triggering captions that boost engagement."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ GPT4Free Error: {e}")
        return "Default caption"

def process_all_videos():
    all_captions = {}

    for keyword_folder in OUTPUT_REELS_DIR.iterdir():
        if not keyword_folder.is_dir():
            continue

        keyword = detect_category_from_folder_name(keyword_folder.name)
        all_captions[keyword] = {}

        for video_file in keyword_folder.glob("*.mp4"):
            prompt = f"Write a short and subconscious-attracting Instagram Reel caption about '{keyword}'. Make it emotional, viral, and highly engaging."
            caption = generate_caption(prompt)
            all_captions[keyword][video_file.name] = caption
            print(f"✅ {video_file.name} → {caption}")

    with open(CAPTIONS_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_captions, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 All captions saved to {CAPTIONS_OUTPUT_FILE}")

if __name__ == "__main__":
    process_all_videos()
