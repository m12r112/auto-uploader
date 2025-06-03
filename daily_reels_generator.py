import os
import json
from pathlib import Path
from datetime import datetime
from moviepy.editor import VideoFileClip, AudioFileClip
from docx import Document
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import shutil

VIDEOS_DIR = Path("videos")
AUDIO_DIR = Path("audio_library")
OUTPUT_DIR = Path("output_reels")
LOG_FILE = Path("Published_Videos_Log.docx")

OUTPUT_DIR.mkdir(exist_ok=True)

# ⛑️ تحميل Google Drive API
SERVICE_ACCOUNT_FILE = "service_account.key"  # تأكد أن هذا الملف مكتوب مسبقاً من GitHub Action
SCOPES = ["https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build("drive", "v3", credentials=creds)

# 🧠 مجلد Google Drive الجذر (AutoUploader)
ROOT_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")

def log_video(keyword, filename):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    if LOG_FILE.exists():
        doc = Document(LOG_FILE)
    else:
        doc = Document()
        doc.add_heading("Published Videos Log", 0)
        table = doc.add_table(rows=1, cols=3)
        hdr = table.rows[0].cells
        hdr[0].text = "Date"
        hdr[1].text = "Keyword"
        hdr[2].text = "Filename"

    table = doc.tables[0]
    row = table.add_row().cells
    row[0].text = now
    row[1].text = keyword
    row[2].text = filename
    doc.save(LOG_FILE)

def get_or_create_folder(name, parent_id=None):
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])
    if folders:
        return folders[0]["id"]
    file_metadata = {'name': name, 'mimeType': 'application/vnd.google-apps.folder'}
    if parent_id:
        file_metadata['parents'] = [parent_id]
    folder = drive_service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def upload_file(file_path, keyword):
    final_reels_root = get_or_create_folder("final_reels", parent_id=ROOT_FOLDER_ID)
    keyword_folder = get_or_create_folder(keyword, parent_id=final_reels_root)

    file_metadata = {
        'name': file_path.name,
        'parents': [keyword_folder]
    }
    media = MediaFileUpload(str(file_path), resumable=True)
    uploaded = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    print(f"☁️ Uploaded to Drive: {file_path.name} (ID: {uploaded['id']})")

def process_video(video_path: Path, keyword: str):
    print(f"🎬 Processing {video_path.name}")
    output_path = OUTPUT_DIR / video_path.name

    try:
        clip = VideoFileClip(str(video_path))
        if clip.audio is not None:
            shutil.copy(str(video_path), str(output_path))
            print(f"🔊 Video has audio, copied: {output_path.name}")
        else:
            audio_file = AUDIO_DIR / f"{keyword}.mp3"
            if not audio_file.exists():
                print(f"❌ No audio found for {keyword}, skipping...")
                return
            audio = AudioFileClip(str(audio_file)).subclip(0, clip.duration)
            clip = clip.set_audio(audio)
            clip.write_videofile(str(output_path), codec="libx264", audio_codec="aac")
            print(f"🔇 Merged silent video with audio: {output_path.name}")

        log_video(keyword, output_path.name)
        upload_file(output_path, keyword)
    except Exception as e:
        print(f"❌ Error processing {video_path.name}: {e}")

def main():
    for keyword_folder in VIDEOS_DIR.iterdir():
        if keyword_folder.is_dir():
            keyword = keyword_folder.name
            for video_file in keyword_folder.glob("*.mp4"):
                process_video(video_file, keyword)

if __name__ == "__main__":
    main()
