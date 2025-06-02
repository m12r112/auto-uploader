
import os
import io
import random
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# إعداد الاتصال بـ Google Drive
SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# المجلد المحلي المؤقت
TEMP_LOCAL_DIR = "audio_temp"

def get_folder_id(folder_name, parent_id=None):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = drive_service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
    folders = results.get('files', [])
    return folders[0]['id'] if folders else None

def download_first_audio(category):
    root_id = get_folder_id("AutoUploader")
    audio_id = get_folder_id("audio", parent_id=root_id)
    category_id = get_folder_id(category, parent_id=audio_id)

    if not category_id:
        print(f"❌ لم يتم العثور على مجلد: {category}")
        return

    query = f"'{category_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and name contains '.mp3'"
    results = drive_service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
    files = results.get('files', [])

    if not files:
        print(f"❌ لا يوجد ملفات mp3 في {category}")
        return

    chosen_file = random.choice(files)
    file_id = chosen_file['id']
    file_name = chosen_file['name']

    local_folder = os.path.join(TEMP_LOCAL_DIR, category)
    os.makedirs(local_folder, exist_ok=True)
    local_path = os.path.join(local_folder, file_name)

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(local_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

    print(f"✅ تم تحميل الصوت: {local_path}")
    return local_path

if __name__ == "__main__":
    for keyword in ["rain", "wind"]:
        download_first_audio(keyword)
