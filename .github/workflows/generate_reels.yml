import os
import io
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# إعداد حساب الخدمة
SERVICE_ACCOUNT_KEY = os.environ["SERVICE_ACCOUNT_KEY"]

with open("service_account.key", "w") as f:
    f.write(SERVICE_ACCOUNT_KEY)

creds = service_account.Credentials.from_service_account_file(
    "service_account.key",
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=creds)

def get_folder_id_by_name(name, parent_id=None):
    query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    return files[0]["id"] if files else None

def download_folder(folder_id, local_path):
    Path(local_path).mkdir(parents=True, exist_ok=True)
    results = drive_service.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id, name, mimeType)"
    ).execute()
    files = results.get("files", [])
    for file in files:
        file_path = os.path.join(local_path, file["name"])
        if file["mimeType"] == "application/vnd.google-apps.folder":
            download_folder(file["id"], file_path)
        else:
            request = drive_service.files().get_media(fileId=file["id"])
            with open(file_path, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
            print(f"✅ Downloaded: {file_path}")

def main():
    print("🔍 Searching for 'AutoUploader'...")
    root_id = get_folder_id_by_name("AutoUploader")
    if not root_id:
        print("❌ 'AutoUploader' folder not found.")
        return

    print("🔍 Searching for 'audio_library' inside AutoUploader...")
    audio_root_id = get_folder_id_by_name("audio_library", parent_id=root_id)
    if not audio_root_id:
        print("❌ 'audio_library' folder not found.")
        return

    print("⬇️ Downloading audio files to local 'audio_library/'...")
    download_folder(audio_root_id, "audio_library")
    print("✅ All audio files downloaded successfully.")

if __name__ == "__main__":
    main()
