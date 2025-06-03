import os
import json
import random
import requests
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 🛠 إعداد المتغيرات من GitHub Secrets
PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]
SERVICE_ACCOUNT_KEY = os.environ["SERVICE_ACCOUNT_KEY"]
DRIVE_FOLDER_ID = os.environ["DRIVE_FOLDER_ID"]

# 🔐 حفظ مفتاح الخدمة مؤقتًا
with open("service_account.key", "w") as f:
    f.write(SERVICE_ACCOUNT_KEY)

# 🧠 اختيار نوعين عشوائيين يوميًا
with open("keywords.json") as f:
    keywords = json.load(f)["keywords"]

selected_keywords = random.sample(keywords, 2)

# 📁 مجلد حفظ الفيديوهات محليًا
videos_dir = Path("videos")
videos_dir.mkdir(exist_ok=True)

# 🔧 إعداد Google Drive API
credentials = service_account.Credentials.from_service_account_file(
    "service_account.key",
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)


def get_pexels_video(keyword):
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={keyword}&orientation=portrait&per_page=10"
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    data = res.json()

    candidates = []
    for video in data.get("videos", []):
        if video["duration"] <= 60:
            for f in video["video_files"]:
                if f["height"] >= 720 and f["width"] < f["height"]:
                    candidates.append(f["link"])
                    break

    return random.choice(candidates) if candidates else None


def get_or_create_folder(folder_name, parent_id):
    """إنشاء مجلد على Google Drive داخل parent_id إذا لم يكن موجودًا"""
    query = f"'{parent_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed = false"
    res = drive_service.files().list(q=query, fields="files(id)").execute()
    files = res.get("files", [])
    if files:
        return files[0]["id"]
    else:
        metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id]
        }
        folder = drive_service.files().create(body=metadata, fields="id").execute()
        return folder["id"]


def upload_to_drive(filepath: Path, parent_folder_id: str, keyword: str):
    # 🔁 تأكد أن مجلد Videos موجود داخل AutoUploader
    videos_root_id = get_or_create_folder("Videos", parent_folder_id)

    # 🔁 تأكد أن مجلد النوع موجود داخل Videos
    keyword_folder_id = get_or_create_folder(keyword, videos_root_id)

    # ⬆️ رفع الملف إلى مجلد النوع
    file_metadata = {
        "name": filepath.name,
        "parents": [keyword_folder_id]
    }
    media = MediaFileUpload(str(filepath), resumable=True)
    drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()


def main():
    for keyword in selected_keywords:
        print(f"[🔍 Pexels] Searching for '{keyword}' …")
        link = get_pexels_video(keyword)
        if not link:
            print(f"[❌] No suitable video found for '{keyword}'")
            continue

        filename = f"{keyword}_{random.randint(1000,9999)}.mp4"
        save_to = videos_dir / keyword / filename
        save_to.parent.mkdir(parents=True, exist_ok=True)

        print(f"[⬇️] Downloading: {link}")
        with requests.get(link, stream=True) as r:
            r.raise_for_status()
            with open(save_to, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        print(f"[✅] Saved: {save_to.name}")
        upload_to_drive(save_to, DRIVE_FOLDER_ID, keyword)


if __name__ == "__main__":
    main()
