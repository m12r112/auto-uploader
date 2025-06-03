import os
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# إعداد حساب الخدمة
SERVICE_ACCOUNT_KEY = os.environ["SERVICE_ACCOUNT_KEY"]

with open("service_account.key", "w") as f:
    f.write(SERVICE_ACCOUNT_KEY)

creds = service_account.Credentials.from_service_account_file(
    "service_account.key",
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=creds)

def get_or_create_folder(name, parent_id=None):
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]

    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    if parent_id:
        metadata["parents"] = [parent_id]

    folder = drive_service.files().create(body=metadata, fields="id").execute()
    return folder["id"]

def upload_to_drive(local_file, parent_id):
    file_metadata = {"name": local_file.name, "parents": [parent_id]}
    media = MediaFileUpload(str(local_file), resumable=True)
    drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"✅ Uploaded: {local_file.name}")

def main():
    OUTPUT_DIR = Path("output_reels")
    if not OUTPUT_DIR.exists():
        print("❌ Folder 'output_reels/' not found.")
        return

    print("🔍 Getting folder 'AutoUploader/final_reels' on Drive...")
    root_id = get_or_create_folder("AutoUploader")
    reels_id = get_or_create_folder("final_reels", parent_id=root_id)

    for video in OUTPUT_DIR.glob("*.mp4"):
        upload_to_drive(video, reels_id)

    print("✅ All reels uploaded to Google Drive successfully.")

if __name__ == "__main__":
    main()
