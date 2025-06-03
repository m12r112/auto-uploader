import os
import json
import requests
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# إعدادات المسارات
TEMP_FOLDER = Path("temp_videos")
TEMP_FOLDER.mkdir(exist_ok=True)

# تحميل بيانات حساب الخدمة من ملف service_account.key
with open("service_account.key", "r") as f:
    key_data = json.load(f)

# إعداد Google Drive API
credentials = service_account.Credentials.from_service_account_info(
    key_data,
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

# مثال على جلب فيديو من Pexels API (اختياري إن كنت تستخدمه)
PEXELS_API_KEY = "YOUR_PEXELS_API_KEY"
PEXELS_HEADERS = {"Authorization": PEXELS_API_KEY}
PEXELS_URL = "https://api.pexels.com/videos/search?query=rain&orientation=portrait&per_page=1"

def download_video(url, filename):
    print(f"⬇️ Downloading: {url}")
    r = requests.get(url, stream=True)
    with open(TEMP_FOLDER / filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✅ Saved: {filename}")

def upload_to_drive(file_path, folder_id=None):
    file_metadata = {
        'name': file_path.name,
        'parents': [folder_id] if folder_id else []
    }
    media = MediaFileUpload(file_path, resumable=True)
    uploaded = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    print(f"📤 Uploaded to Drive: {uploaded.get('id')}")

# مثال تنفيذ:
def main():
    # يمكنك استبدال هذا بقائمة روابط فعلية
    video_url = "https://player.vimeo.com/external/441183813.sd.mp4?s=..."  # استبدله برابط صالح
    filename = "rain_sample.mp4"

    download_video(video_url, filename)
    upload_to_drive(TEMP_FOLDER / filename)

if __name__ == "__main__":
    main()
