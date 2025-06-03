import os
import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 📝 اسم ملف الكابتشنات
CAPTION_FILE = "captions.json"
if not os.path.exists(CAPTION_FILE):
    print(f"❌ الملف {CAPTION_FILE} غير موجود.")
    exit(1)

# 🔐 تحميل بيانات حساب الخدمة
key_json = os.environ.get("SERVICE_ACCOUNT_KEY")
if not key_json:
    raise Exception("❌ SERVICE_ACCOUNT_KEY غير موجود في البيئة.")

with open("service_account.key", "w") as f:
    f.write(key_json)

with open("service_account.key", "r") as f:
    key_data = json.load(f)

credentials = service_account.Credentials.from_service_account_info(
    key_data,
    scopes=["https://www.googleapis.com/auth/drive"]
)

drive_service = build("drive", "v3", credentials=credentials)

def get_or_create_folder(name, parent_id=None):
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = drive_service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    folders = results.get("files", [])
    if folders:
        return folders[0]['id']

    file_metadata = {'name': name, 'mimeType': 'application/vnd.google-apps.folder'}
    if parent_id:
        file_metadata['parents'] = [parent_id]
    folder = drive_service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def upload_caption_file():
    root_id = get_or_create_folder("AutoUploader")
    captions_folder_id = get_or_create_folder("captions", parent_id=root_id)

    file_metadata = {
        "name": CAPTION_FILE,
        "parents": [captions_folder_id]
    }
    media = MediaFileUpload(CAPTION_FILE, resumable=True, mimetype="application/json")
    uploaded = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    print(f"✅ تم رفع {CAPTION_FILE} إلى Google Drive → ID: {uploaded['id']}")

if __name__ == "__main__":
    upload_caption_file()
