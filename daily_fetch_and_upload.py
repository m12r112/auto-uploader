import os
import json
import random
import requests
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# إعداد مجلدات التخزين محليًا
VIDEO_ROOT = Path("videos")
VIDEO_ROOT.mkdir(exist_ok=True)

# تحميل الكلمات المفتاحية
with open("keywords.json") as f:
    keywords = json.load(f)["keywords"]

# اختيار كلمتين عشوائيتين
selected_keywords = random.sample(keywords, k=2)

# قراءة المفاتيح من environment
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
if not PEXELS_API_KEY:
    raise Exception("❌ PEXELS_API_KEY not found.")

DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")
if not DRIVE_FOLDER_ID:
    raise Exception("❌ DRIVE_FOLDER_ID not found.")

PEXELS_API_URL = "https://api.pexels.com/videos/search"
headers = {"Authorization": PEXELS_API_KEY}

def fetch_video_url(keyword):
    print(f"🔍 [Pexels] Searching for '{keyword}'...")
    params = {"query": keyword, "per_page": 10}
    response = requests.get(PEXELS_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        for video in data.get("videos", []):
            for file in video.get("video_files", []):
                # تخفيف الفلترة: نقبل 720p فما فوق
                if file.get("width") >= 720 and file.get("height") >= 720:
                    print(f"🔗 Found URL for '{keyword}': {file['link']}")
                    return file["link"]
    print(f"❌ No suitable video found for '{keyword}'")
    return None

def download_video(url, save_path):
    print(f"⬇️ Downloading to {save_path} ...")
    r = requests.get(url, stream=True)
    with open(save_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✅ Downloaded: {save_path}")

def get_or_create_folder(drive_service, parent_id, folder_name):
    print(f"🗂️ Checking for folder '{folder_name}' in parent '{parent_id}' ...")
    query = (
        f"mimeType='application/vnd.google-apps.folder' "
        f"and name='{folder_name}' "
        f"and '{parent_id}' in parents "
        f"and trashed=false"
    )
    results = drive_service.files().list(
        q=query, spaces="drive", fields="files(id, name)"
    ).execute()
    items = results.get("files", [])
    if items:
        folder_id = items[0]["id"]
        print(f"🔎 Found existing folder '{folder_name}' (ID = {folder_id})")
        return folder_id

    print(f"➕ Folder '{folder_name}' not found. Creating it...")
    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id]
    }
    folder = drive_service.files().create(body=file_metadata, fields="id").execute()
    new_id = folder.get("id")
    print(f"✅ Created folder '{folder_name}' with ID = {new_id}")
    return new_id

def upload_to_drive(local_file_path, parent_folder_id, keyword):
    print(f"☁️ Uploading '{local_file_path}' to Drive under keyword '{keyword}' ...")
    creds = service_account.Credentials.from_service_account_file(
        "service_account.key",
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    drive_service = build("drive", "v3", credentials=creds)

    try:
        folder_id = get_or_create_folder(drive_service, parent_folder_id, keyword)
    except HttpError as e:
        print(f"❌ Error fetching/creating folder '{keyword}': {e}")
        print(str(e))
        return

    file_metadata = {
        "name": os.path.basename(local_file_path),
        "parents": [folder_id]
    }
    media = MediaFileUpload(local_file_path, mimetype="video/mp4")
    try:
        uploaded = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, name"
        ).execute()
        print(f"✅ Uploaded to Drive: {uploaded['name']} (ID = {uploaded['id']}), in folder '{keyword}'")
    except HttpError as e:
        print(f"❌ Error uploading file '{local_file_path}': {e}")
        print(str(e))

def main():
    print(f"📁 Parent Drive folder ID = {DRIVE_FOLDER_ID}")
    for keyword in selected_keywords:
        print(f"\n🔍 Processing keyword: {keyword}")
        video_url = fetch_video_url(keyword)
        if not video_url:
            continue

        keyword_dir = VIDEO_ROOT / keyword
        keyword_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{keyword}_{random.randint(1000,9999)}.mp4"
        save_path = keyword_dir / filename

        download_video(video_url, save_path)
        upload_to_drive(str(save_path), DRIVE_FOLDER_ID, keyword)

if __name__ == "__main__":
    main()
