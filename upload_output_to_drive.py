import os
import json
import tempfile
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# استخراج بيانات JSON من GitHub Secret
service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])

# إنشاء ملف مؤقت لتمريره إلى Google
with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as f:
    json.dump(service_account_info, f)
    SERVICE_ACCOUNT_FILE = f.name

SCOPES = ['https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

OUTPUT_DIR = "output_reels"

def get_or_create_folder(name, parent_id=None):
    """Return folder ID by name, or create it if it doesn't exist."""
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get('files', [])
    if folders:
        return folders[0]['id']
    
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]
    folder = drive_service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def upload_file(file_path, parent_id):
    """Upload a file to a specified folder in Google Drive."""
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [parent_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    uploaded = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"✅ تم رفع الملف: {file_path}")

def upload_output_videos():
    root_id = get_or_create_folder("AutoUploader")
    final_videos_id = get_or_create_folder("final_videos", parent_id=root_id)

    for keyword_folder in Path(OUTPUT_DIR).iterdir():
        if keyword_folder.is_dir():
            keyword = keyword_folder.name
            keyword_drive_id = get_or_create_folder(keyword, parent_id=final_videos_id)
            for video_file in keyword_folder.glob("*.mp4"):
                upload_file(str(video_file), parent_id=keyword_drive_id)

if __name__ == "__main__":
    upload_output_videos()
