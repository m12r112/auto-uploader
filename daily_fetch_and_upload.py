import os
import json
import requests
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TEMP_FOLDER = Path("temp_videos")
TEMP_FOLDER.mkdir(exist_ok=True)

def setup_drive():
    key_json = os.environ.get("SERVICE_ACCOUNT_KEY")
    if not key_json:
        raise Exception("❌ SERVICE_ACCOUNT_KEY not found. Did you forget to add it as a GitHub Secret?")
    
    with open("service_account.key", "w") as f:
        f.write(key_json)

    with open("service_account.key", "r") as f:
        key_data = json.load(f)

    credentials = service_account.Credentials.from_service_account_info(
        key_data,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=credentials)

def download_video(url, filename):
    print(f"⬇️ Downloading: {url}")
    r = requests.get(url, stream=True)
    with open(TEMP_FOLDER / filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✅ Saved: {filename}")

def upload_to_drive(service, file_path, folder_id=None):
    file_metadata = {
        'name': file_path.name,
        'parents': [folder_id] if folder_id else []
    }
    media = MediaFileUpload(file_path, resumable=True)
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    print(f"📤 Uploaded to Drive: {uploaded.get('id')}")

def main():
    drive_service = setup_drive()
    
    # مثال لرابط فيديو (غيّره حسب مشروعك)
    video_url = "https://player.vimeo.com/external/441183813.sd.mp4?s=..."
    filename = "sample.mp4"

    download_video(video_url, filename)
    upload_to_drive(drive_service, TEMP_FOLDER / filename)

if __name__ == "__main__":
    main()
