import os
import io
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# 🔐 تحميل مفتاح الخدمة من المتغير البيئي
key_json = os.environ["SERVICE_ACCOUNT_KEY"]
with open("service_account.key", "w") as f:
    f.write(key_json)

credentials = service_account.Credentials.from_service_account_file(
    "service_account.key",
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

# 🧭 دالة للبحث عن مجلد وفق المسار الكامل
def find_folder_path(path_list):
    parent_id = "root"
    for name in path_list:
        query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and '{parent_id}' in parents"
        res = drive_service.files().list(q=query, fields="files(id, name)").execute()
        folders = res.get("files", [])
        if not folders:
            print(f"❌ لم يتم العثور على المجلد: {name}")
            return None
        parent_id = folders[0]["id"]
    return parent_id

# 🔍 تحديد مجلد AutoUploader/Videos
videos_folder_id = find_folder_path(["AutoUploader", "Videos"])

if not videos_folder_id:
    print("❌ لم يتم العثور على المسار AutoUploader/Videos")
    exit(1)

# 📂 الحصول على كل المجلدات الفرعية (أنواع الفيديو)
subfolders = drive_service.files().list(
    q=f"'{videos_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'",
    fields="files(id, name)"
).execute().get("files", [])

for folder in subfolders:
    folder_name = folder["name"]
    folder_id = folder["id"]
    print(f"📂 يعالج النوع: {folder_name}")

    # إنشاء المجلد المحلي
    local_folder = Path("videos") / folder_name
    local_folder.mkdir(parents=True, exist_ok=True)

    # 🧲 تحميل كل ملفات الفيديو داخل المجلد الفرعي
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
