import os
import json
import random
import requests
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 📁 إعداد مجلدات التخزين
VIDEO_ROOT = Path("videos")
VIDEO_ROOT.mkdir(exist_ok=True)

# 📥 تحميل الكلمات المفتاحية
with open("keywords.json") as f:
    keywords = json.load(f)["keywords"]

# 🧠 اختيار كلمتين عشوائيتين
selected_keywords = random.sample(keywords, k=2)

# 🔐 إعداد مفاتيح API
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
if not PEXELS_API_KEY:
    raise Exception("❌ PEXELS_API_KEY not found in environment.")

DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")
if not DRIVE_FOLDER_ID:
    raise Exception("❌ DRIVE_FOLDER_ID not found in environment.")

PEXELS_API_URL = "https://api.pexels.com/videos/search"
headers = {"Authorization": PEXELS_API_KEY}

# 🌐 جلب رابط الفيديو من Pexels
def fetch_video_url(keyword):
    params = {"query": keyword, "per_page": 5}
    response = requests.get(PEXELS_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        for video in data.get("videos", []):
            for file in video.get("video_files", []):
                if file.get("width") == 1080 and file.get("height") >= 1080 and file.get("quality") == "sd":
                    return file["link"]
    return None

# 💾 تحميل الفيديو محليًا
def download_video(url, save_path):
    r = requests.get(url, stream=True)
    with open(save_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✅ Downloaded: {save_path}")

# ☁️ رفع الفيديو إلى Google Drive
def upload_to_drive(local_file_path, folder_id):
    # تحميل بيانات اعتماد حساب الخدمة
    creds = service_account.Credentials.from_service_account_file(
        "service_account.key",
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    drive_service = build("drive", "v3", credentials=creds)

    # إعداد معلومات الملف
    file_metadata = {
        "name": os.path.basename(local_file_path),
        "parents": [folder_id]
    }
    media = MediaFileUpload(local_file_path, mimetype="video/mp4")
    uploaded = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name"
    ).execute()

    print(f"✅ Uploaded to Drive: {uploaded['name']} ({uploaded['id']})")

# ▶️ الدالة الرئيسية
def main():
    for keyword in selected_keywords:
        print(f"🔍 Searching for: {keyword}")
        video_url = fetch_video_url(keyword)
        if not video_url:
            print(f"❌ No video found for keyword: {keyword}")
            continue

        keyword_dir = VIDEO_ROOT / keyword
        keyword_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{keyword}_{random.randint(1000,9999)}.mp4"
        save_path = keyword_dir / filename

        download_video(video_url, save_path)
        upload_to_drive(str(save_path), DRIVE_FOLDER_ID)

if __name__ == "__main__":
    main()
