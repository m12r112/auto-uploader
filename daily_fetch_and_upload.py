import os
import json
import requests
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ✅ استخدام Secret الصحيح كما في GitHub
key_json = os.environ["SERVICE_ACCOUNT_KEY"]
with open("service_account.key", "w") as f:
    f.write(key_json)

# إعداد Google Drive API
with open("service_account.key", "r") as f:
    key_data = json.load(f)

credentials = service_account.Credentials.from_service_account_info(
    key_data,
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

# إعداد مجلد مؤقت
TEMP_FOLDER = Path("temp_videos")
TEMP_FOLDER.mkdir(exist_ok=True)

# تحميل فيديو من رابط (مثال)
def download_video(url, filename):
    print(f"⬇️ Downloading: {url}")
    r = requests.get(url, stream=True)
    with open(TEMP_FOLDER / filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✅ Saved: {filename}")

# رفع الفيديو إلى Google Drive
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

# تنفيذ العملية الكاملة
def main():
    video_url = "https://player.vimeo.com/external/441183813.sd.mp4?s=..."  # استبدله برابط حقيقي
    filename = "sample.mp4"
    download_video(video_url, filename)
    upload_to_drive(TEMP_FOLDER / filename)

if __name__ == "__main__":
    main()
