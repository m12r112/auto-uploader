import os
import io
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# 🔐 تحميل مفتاح الخدمة
key_json = os.environ["SERVICE_ACCOUNT_KEY"]
with open("service_account.key", "w") as f:
    f.write(key_json)

credentials = service_account.Credentials.from_service_account_file(
    "service_account.key",
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

# 🗂️ البحث عن مجلد Videos داخل AutoUploader
def find_folder(name, parent=None):
    q = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
    if parent:
        q += f" and '{parent}' in parents"
    else:
        q += " and 'root' in parents"

    res = drive_service.files().list(q=q, fields="files(id, name)").execute()
    folders = res.get("files", [])
    return folders[0]["id"] if folders else None

main_folder_id = find_folder("AutoUploader")
videos_folder_id = find_folder("Videos", parent=main_folder_id)

if not videos_folder_id:
    print("❌ لم يتم العثور على مجلد AutoUploader/Videos")
    exit(1)

# 🔍 جلب كل المجلدات الفرعية داخل Videos
subfolders = drive_service.files().list(
    q=f"'{videos_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'",
    fields="files(id, name)"
).execute().get("files", [])

for folder in subfolders:
    folder_name = folder["name"]
    folder_id = folder["id"]
    print(f"📂 يعالج النوع: {folder_name}")

    # إنشاء مجلد محلي
    local_folder = Path("videos") / folder_name
    local_folder.mkdir(parents=True, exist_ok=True)

    # جلب الفيديوهات داخل المجلد
    videos = drive_service.files().list(
        q=f"'{folder_id}' in parents and mimeType contains 'video'",
        fields="files(id, name)"
    ).execute().get("files", [])

    for video in videos:
        file_id = video["id"]
        file_name = video["name"]
        target_path = local_folder / file_name

        if target_path.exists():
            print(f"⏭️ موجود مسبقًا: {file_name}")
            continue

        print(f"⬇️ تنزيل: {file_name}")
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(target_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
