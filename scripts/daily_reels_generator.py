from pathlib import Path
import os
import json
import requests
import random
from moviepy.editor import VideoFileClip, AudioFileClip

# اقرأ التوكن المحدّث من ملف خارجي
INSTAGRAM_ACCESS_TOKEN = Path("latest_token.txt").read_text().strip()

# إعدادات المسارات
with open("settings.json") as f:
    settings = json.load(f)

FINAL_REELS = Path(settings["final_reels_dir"])
LOG_FILE = Path(settings["uploaded_log_file"])

def was_uploaded(video_path):
    """تحقق مما إذا تم نشر هذا الفيديو مسبقًا"""
    if not os.path.exists(LOG_FILE):
        return False
    return video_path.name in LOG_FILE.read_text(encoding="utf-8")

def post_to_instagram(video_path):
    print("🎬 جاري النشر:", video_path)
    print("🔐 باستخدام التوكن:", INSTAGRAM_ACCESS_TOKEN[:10], "...")

    # يمكنك هنا لاحقًا استدعاء Instagram Graph API لرفع الفيديو
    # (تم ترك النشر الفعلي كتعليق)

def main():
    for file in FINAL_REELS.iterdir():
        if file.suffix != ".mp4" or was_uploaded(file):
            continue
        post_to_instagram(file)

        # سجل الفيديو كـ "تم نشره"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(file.name + "\n")

if __name__ == "__main__":
    main()
