import os
import json
import random
from pathlib import Path
from g4f.client import Client  # تأكد من تثبيت g4f
from moviepy.editor import VideoFileClip

# إعداد المسارات
OUTPUT_REELS = Path("output_reels")
client = Client()

def get_video_duration(video_path):
    try:
        clip = VideoFileClip(str(video_path))
        duration = clip.duration
        clip.close()
        return duration
    except Exception as e:
        print(f"⚠️ Error reading {video_path.name}: {e}")
        return None

def extract_keyword_from_filename(filename):
    return filename.stem.split("_")[0].lower()

def generate_caption(keyword, duration_sec):
    prompt = (
        f"Write a short, emotional and hypnotic caption for a short video about '{keyword}', "
        f"that lasts around {int(duration_sec)} seconds. "
        f"It should subconsciously influence the viewer to watch till the end and follow the page. "
        f"The tone must be poetic, touching, and addictive. Language: English."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Error generating caption for '{keyword}': {e}")
        return None

def main():
    for video_path in OUTPUT_REELS.glob("*.mp4"):
        keyword = extract_keyword_from_filename(video_path)
        duration = get_video_duration(video_path)
        if duration is None:
            continue

        caption_path = video_path.with_suffix(".txt")
        if caption_path.exists():
            print(f"⏭️ Skipping {video_path.name}, caption already exists.")
            continue

        print(f"✍️ Generating caption for {video_path.name}...")
        caption = generate_caption(keyword, duration)
        if caption:
            caption_path.write_text(caption, encoding="utf-8")
            print(f"✅ Saved caption: {caption_path.name}")

if __name__ == "__main__":
    main()
