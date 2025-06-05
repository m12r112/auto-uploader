import os
import io
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# إعداد المفتاح
key_json = os.environ["SERVICE_ACCOUNT_KEY"]
with open("service_account.key", "w") as f:
    f.write(key_json)

credentials = service_account.Credentials.from_service_account_file(
    "service_account.key",
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

# ✅ نستخدم ID مجلد Videos مباشرة
videos_folder_id = "1d2MrcTUp0RmRPO7fU3V85NrrOXGJq04U"

# جلب كل المجلدات الفرعية داخل Videos
subfolders = drive_service.files().list(
    q=f"'{videos_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'",
    fields="files(id, name)"
).execute().get("files", [])

print(f"📂 تم العثور على {len(subfolders)} مجلدات فرعية داخل Videos.")

for folder in subfolders:
    folder_name = folder["name"]
    folder_id = folder["id"]
    print(f"🔍 يعالج المجلد: {folder_name}")

    local_folder = Path("videos") / folder_name
    local_folder.mkdir(parents=True, exist_ok=True)

    # تحميل الفيديوهات
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

        print(f"⬇️ تحميل: {file_name}")
        request = drive_service.files().get_media(fileId=file_id)
        with io.FileIO(target_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
