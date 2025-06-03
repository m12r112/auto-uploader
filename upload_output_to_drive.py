import os
import io
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# تحميل الإعدادات
import json
with open("settings.json") as f:
    settings = json.load(f)

SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']
OUTPUT_DIR = "output_reels"
CAPTION_DIR = "captions"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

def get_folder_id(folder_name, parent_id=None):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get('files', [])
    return folders[0]['id'] if folders else None

def upload_file_to_drive(file_path, parent_id):
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [parent_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return uploaded_file.get('id')

def upload_output_videos():
    main_folder_id = get_folder_id(settings["main_drive_folder"])
    output_folder_id = get_folder_id("Output", parent_id=main_folder_id)
    publish_queue_id = get_folder_id("PublishQueue", parent_id=main_folder_id)

    for keyword_folder in Path(OUTPUT_DIR).iterdir():
        if not keyword_folder.is_dir():
            continue

        for file in keyword_folder.iterdir():
            if not file.name.endswith(".mp4"):
                continue

            # رفع الفيديو إلى مجلد Output
            upload_file_to_drive(str(file), output_folder_id)

            # البحث عن ملف الوصف المقابل
            caption_name = file.name.replace(".mp4", ".txt")
            caption_path = Path(CAPTION_DIR) / keyword_folder.name / caption_name

            # رفع الفيديو + الوصف إلى PublishQueue
            upload_file_to_drive(str(file), publish_queue_id)
            if caption_path.exists():
                upload_file_to_drive(str(caption_path), publish_queue_id)

            # حذف الملف المحلي لتوفير المساحة
            os.remove(file)
            if caption_path.exists():
                os.remove(caption_path)

if __name__ == "__main__":
    upload_output_videos()
