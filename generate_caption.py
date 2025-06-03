import os
import json
from pathlib import Path
from g4f.client import Client

OUTPUT_DIR = Path("output_reels")
CAPTIONS_OUTPUT_FILE = "captions.json"
client = Client()
captions = {}

def generate_caption(keyword):
    prompt = f"""
    Write a short, engaging Instagram Reels caption about "{keyword}" that triggers subconscious emotion and boosts interaction. Use 1 emoji. No hashtags.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a social media expert who writes viral captions."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ GPT Error for {keyword}: {e}")
        return f"{keyword.title()} video."

def main():
    for keyword_folder in OUTPUT_DIR.iterdir():
        if not keyword_folder.is_dir():
            continue

        keyword = keyword_folder.name.strip().lower()

        for video_file in keyword_folder.glob("*.mp4"):
            if video_file.name in captions:
                continue

            print(f"📝 Generating caption for {video_file.name} (keyword: {keyword})")
            caption = generate_caption(keyword)

            captions[video_file.name] = {
                "keyword": keyword,
                "caption": caption
            }

    with open(CAPTIONS_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(captions, f, indent=2, ensure_ascii=False)

    print(f"✅ Captions saved to {CAPTIONS_OUTPUT_FILE}")

if __name__ == "__main__":
    main()
