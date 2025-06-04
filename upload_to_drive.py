import os
import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

OUTPUT_DIR = Path("final_reels")
LOG_FILE = Path("Published_Videos_Log.txt")

def setup_drive():
    key_json = os.environ.get("SERVICE_ACCOUNT_KEY")
    if not key_json:
        raise Exception("❌ SERVICE_ACCOUNT_KEY not found in environment.")
    
    key_data = json.loads(key_json)
    credentials = service_account.Credentials.from_service_account_info(
        key_data, scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=credentials)

def get_or_create_folder(service, folder_name, parent_id=None):
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']

    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]

    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def make_file_public(service, file_id):
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    service.permissions().create(fileId=file_id, body=permission).execute()

def get_public_url(file_id):
    return f"https://drive.google.com/uc?id={file_id}&export=download"

def upload_file(service, file_path, parent_folder_id):
    file_metadata = {
        'name': file_path.name,
        'parents': [parent_folder_id]
    }
    media = MediaFileUpload(str(file_path), resumable=True)
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = uploaded.get("id")
    make_file_public(service, file_id)
    public_url = get_public_url(file_id)

    with open(LOG_FILE, "a") as log:
        log.write(f"{file_path.name}\n")

    print(f"{public_url}|{file_id}")
    return public_url, file_id

def upload_all_videos(service):
    auto_folder = get_or_create_folder(service, "AutoUploader")
    reels_folder = get_or_create_folder(service, "UploadedReels", parent_id=auto_folder)

    print("📂 Scanning for videos in:", OUTPUT_DIR)
    for video_file in OUTPUT_DIR.glob("*.mp4"):
        url, fid = upload_file(service, video_file, reels_folder)
        print(f"{url}|{fid}")
        break  # فقط أول فيديو

def main():
    service = setup_drive()
    upload_all_videos(service)

if __name__ == "__main__":
    main()
