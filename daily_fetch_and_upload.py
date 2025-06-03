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
    keywords = json.load(f)["keywords"]  # ✅ هذا هو التعديل لتوافق ملفك

selected_keywords = random.sample(keywords, 2)

# 📁 مجلد حفظ الفيديوهات
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

    # 🔍 اختار فيديو بدقة 720p أو أعلى ومدته ≤ 60 ثانية
    candidates = []
    for video in data.get("videos", []):
        if video["duration"] <= 60:
            for f in video["video_files"]:
                if f["height"] >= 720 and f["width"] < f["height"]:  # عمودي
                    candidates.append(f["link"])
                    break

    return random.choice(candidates) if candidates else None


def upload_to_drive(filepath: Path, parent_folder_id: str, keyword: str):
    # تحقق إن كان مجلد النوع موجودًا داخل Google Drive، وإن لم يكن فأنشئه
    folder_name = keyword
    folder_id = None

    query = f"'{parent_folder_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed = false"
    response = drive_service.files().list(q=query, fields="files(id)").execute()
    files = response.get("files", [])
    if files:
        folder_id = files[0]["id"]
    else:
        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_folder_id]
        }
        folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
        folder_id = folder["id"]

    file_metadata = {
        "name": filepath.name,
        "parents": [folder_id]
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

        # تحميل الفيديو
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

        # رفع الفيديو إلى Google Drive
        upload_to_drive(save_to, DRIVE_FOLDER_ID, keyword)


if __name__ == "__main__":
    main()
