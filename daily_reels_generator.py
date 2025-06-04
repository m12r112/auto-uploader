from pathlib import Path
import os
import json
import random
from googleapiclient import discovery
from google.oauth2 import service_account
from moviepy.editor import VideoFileClip, AudioFileClip

# 🟩 قراءة التوكن المحدّث من الملف الذي أنشأه refresh_token.py
INSTAGRAM_ACCESS_TOKEN = Path("latest_token.txt").read_text().strip()

with open("settings.json") as f:
    settings = json.load(f)

FINAL_REELS = Path(settings["final_reels_dir"])
LOG_FILE = Path(settings["uploaded_log_file"])

def not_already_uploaded(file):
    if not os.path.exists(LOG_FILE):
        return True
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return file not in f.read()

def upload_to_instagram(video_path):
    print("✅ سيتم رفع الفيديو:", video_path)
    print("🔑 التوكن المستخدم:", INSTAGRAM_ACCESS_TOKEN[:10], "...")
    # هنا تضع كود رفع الفيديو إلى Instagram Graph API لاحقًا

def main():
    for file in os.listdir(FINAL_REELS):
        if file.endswith(".mp4") and not_already_uploaded(file):
            video_path = FINAL_REELS / file
            upload_to_instagram(video_path)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(file + "\n")

if __name__ == "__main__":
    main()
