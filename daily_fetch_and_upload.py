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
    params = {"query": keyword, "per_page": 20}
    response = requests.get(PEXELS_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        candidates = [file["link"] for video in data.get("videos", []) for file in video.get("video_files", [])
                      if file.get("width") == 1080 and file.get("height") >= 1080 and file.get("quality") == "sd"]
        if candidates:
            return random.choice(candidates)
    return None

def download_video(url, save_path):
    r = requests.get(url, stream=True)
    with open(save_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✅ Downloaded: {save_path}")

def get_or_create_folder(drive_service, parent_id, folder_name):
    query = (
        f"mimeType='application/vnd.google-apps.folder' "
        f"and name='{folder_name}' "
        f"and '{parent_id}' in parents "
        f"and trashed=false"
    )
    results = drive_service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)"
    ).execute()
    items = results.get("files", [])
    if items:
        return items[0]["id"]

    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id]
    }
    folder = drive_service.files().create(body=file_metadata, fields="id").execute()
    return folder.get("id")

def upload_to_drive(local_file_path, parent_folder_id, keyword):
    print(f"☁️ Uploading '{local_file_path}' to Drive under keyword '{keyword}' ...")
    creds = service_account.Credentials.from_service_account_file(
        "service_account.key",
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    drive_service = build("drive", "v3", credentials=creds)

    try:
        # إنشاء مجلد Videos داخل AutoUploader
        videos_root_id = get_or_create_folder(drive_service, parent_folder_id, "Videos")

        # ثم مجلد النوع مثل rain أو thunder
        keyword_folder_id = get_or_create_folder(drive_service, videos_root_id, keyword)
    except HttpError as e:
        print(f"❌ Error creating folders: {e}")
        return

    file_metadata = {
        "name": os.path.basename(local_file_path),
        "parents": [keyword_folder_id]
    }
    media = MediaFileUpload(local_file_path, mimetype="video/mp4")

    try:
        uploaded = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, name"
        ).execute()
        print(f"✅ Uploaded to Drive: {uploaded['name']} (ID: {uploaded['id']}) in '{keyword}' folder")
    except HttpError as e:
        print(f"❌ Error uploading file: {e}")

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
        upload_to_drive(str(save_path), DRIVE_FOLDER_ID, keyword)

if __name__ == "__main__":
    main()
