import os
import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ⛑️ تحميل مفتاح الخدمة من Secret
key_json = os.environ["SERVICE_ACCOUNT_KEY"]
with open("service_account.key", "w") as f:
    f.write(key_json)

# 🎯 إعداد Google Drive API
with open("service_account.key", "r") as f:
    key_data = json.load(f)

credentials = service_account.Credentials.from_service_account_info(
    key_data,
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

# 🗂️ مجلد الفيديوهات النهائية
OUTPUT_DIR = Path("output_reels")

def upload_file(file_path):
    file_metadata = {
        'name': file_path.name
    }
    media = MediaFileUpload(str(file_path), resumable=True)
    uploaded = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    print(f"✅ Uploaded: {file_path.name} (Drive ID: {uploaded['id']})")

def upload_all_videos():
    for keyword_folder in OUTPUT_DIR.iterdir():
        if not keyword_folder.is_dir():
            continue
        for video_file in keyword_folder.glob("*.mp4"):
            upload_file(video_file)

if __name__ == "__main__":
    upload_all_videos()
