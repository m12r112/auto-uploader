import os
import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# إعداد حساب الخدمة
key_json = os.environ["SERVICE_ACCOUNT_KEY"]
with open("service_account.key", "w") as f:
    f.write(key_json)

credentials = service_account.Credentials.from_service_account_file(
    "service_account.key",
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

# إعداد المسارات
FOLDER_NAME = "AutoUploader"
SUBFOLDER_NAME = "final_reels"
LOCAL_FOLDER = Path("final_reels")
LOCAL_FOLDER.mkdir(exist_ok=True)

# 🔍 أول فيديو جاهز للنشر
video_files = list(LOCAL_FOLDER.glob("*.mp4"))
if not video_files:
    print("❌ لا يوجد فيديوهات في final_reels/")
    exit(1)

video_path = video_files[0]
video_name = video_path.name

# 🔎 العثور أو إنشاء مجلدات Drive
def find_or_create_folder(name, parent_id=None):
    q = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        q += f" and '{parent_id}' in parents"
    else:
        q += " and 'root' in parents"

    results = drive_service.files().list(q=q, fields="files(id, name)").execute()
    folders = results.get("files", [])
    if folders:
        return folders[0]["id"]

    metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        metadata["parents"] = [parent_id]

    folder = drive_service.files().create(body=metadata, fields="id").execute()
    return folder["id"]

main_folder_id = find_or_create_folder(FOLDER_NAME)
target_folder_id = find_or_create_folder(SUBFOLDER_NAME, parent_id=main_folder_id)

# ⬆️ رفع الفيديو
file_metadata = {"name": video_name, "parents": [target_folder_id]}
media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
uploaded = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
file_id = uploaded["id"]

# 🌍 جعل الفيديو عام
drive_service.permissions().create(
    fileId=file_id,
    body={"type": "anyone", "role": "reader"},
    fields="id"
).execute()

video_url = f"https://drive.google.com/uc?id={file_id}"

# ✅ طباعة النتائج
print("VIDEO_PUBLIC_URL =", video_url)
print("DRIVE_FILE_ID =", file_id)

# لـ GitHub Actions
print(f"::set-output name=video_url::{video_url}")
print(f"::set-output name=drive_file_id::{file_id}")
