# ✅ daily_fetch_and_upload.py (مُحدَّث)

import os
import requests
import random
from moviepy.editor import VideoFileClip
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json

# 🗝️ تحميل مفتاح الخدمة
SERVICE_ACCOUNT_KEY = os.environ["SERVICE_ACCOUNT_KEY"]
with open("service_account.key", "w") as f:
    f.write(SERVICE_ACCOUNT_KEY)

creds = service_account.Credentials.from_service_account_file(
    "service_account.key",
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=creds)

# 🔁 تحميل كلمات البحث من keywords.json
with open("keywords.json") as f:
    keywords = json.load(f)["keywords"]

PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]
PEXELS_API_URL = "https://api.pexels.com/videos/search"

headers = {"Authorization": PEXELS_API_KEY}

# 🧠 اختيار كلمتين عشوائيًا يوميًا
random_keywords = random.sample(keywords, 2)

for keyword in random_keywords:
    print(f"🔍 يبحث عن: {keyword}")
    response = requests.get(PEXELS_API_URL, params={"query": keyword, "orientation": "portrait", "per_page": 10}, headers=headers)
    results = response.json().get("videos", [])

    Path(f"videos/{keyword}").mkdir(parents=True, exist_ok=True)

    count = 0
    for video in results:
        if count >= 2:
            break
        video_url = video["video_files"][-1]["link"]  # أعلى جودة غالبًا
        video_id = video["id"]
        video_path = f"videos/{keyword}/{keyword}_{video_id}.mp4"

        # 💾 تحميل الفيديو
        try:
            r = requests.get(video_url, timeout=30)
            with open(video_path, "wb") as f:
                f.write(r.content)
        except Exception as e:
            print(f"❌ فشل التحميل: {e}")
            continue

        # ✅ تحقق من الطول والعمودية والصوت
        try:
            clip = VideoFileClip(video_path)
            if clip.h > clip.w and clip.audio is not None:
                print(f"✅ مقبول: {video_path}")
                count += 1
            else:
                print(f"⛔ مستبعد (ليس عمودي أو صامت): {video_path}")
                os.remove(video_path)
        except Exception as e:
            print(f"⚠️ خطأ عند التحقق: {e}")
            if os.path.exists(video_path):
                os.remove(video_path)
            continue

# ✅ سيتم لاحقًا نسخ 2 فقط من هذه الفيديوهات إلى output_reels/
