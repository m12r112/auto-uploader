from pathlib import Path
import os
import json
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from moviepy.editor import VideoFileClip, AudioFileClip
import random

# ✅ قراءة التوكن من الملف الذي يتم تحديثه تلقائيًا
INSTAGRAM_ACCESS_TOKEN = Path("latest_token.txt").read_text().strip()

# إعدادات المسارات
with open("settings.json") as f:
    settings = json.load(f)

FINAL_REELS_DIR = settings["final_reels_dir"]
LOG_FILE = settings["published_log_file"]

def read_uploaded_videos():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.read().splitlines()

def upload_to_instagram(video_path):
    print(f"⬆️ جاري رفع الفيديو: {video_path}")
    print(f"🔐 باستخدام التوكن: {INSTAGRAM_ACCESS_TOKEN[:10]}...")

    # يمكنك هنا كتابة كود رفع الفيديو إلى Instagram Graph API باستخدام requests

def main():
    uploaded = set(read_uploaded_videos())

    for file in os.listdir(FINAL_REELS_DIR):
        if file.endswith(".mp4") and file not in uploaded:
            full_path = os.path.join(FINAL_REELS_DIR, file)
            upload_to_instagram(full_path)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(file + "\n")
            break

if __name__ == "__main__":
    main()
