import os
import json
import requests
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
if not access_token:
    print("❌ لم يتم العثور على التوكن.")
    exit(1)

ig_user_id = os.environ.get("IG_USER_ID")
fb_page_id = os.environ.get("FB_PAGE_ID")
video_url = os.environ.get("VIDEO_PUBLIC_URL")
file_id = os.environ.get("DRIVE_FILE_ID")

if not ig_user_id or not fb_page_id or not video_url:
    print("❌ تأكد من IG_USER_ID و FB_PAGE_ID و VIDEO_PUBLIC_URL.")
    exit(1)

reels_folder = Path("final_reels")
video_files = list(reels_folder.glob("*.mp4"))
if not video_files:
    print("❌ لا يوجد فيديو للنشر.")
    exit(0)

video_path = video_files[0]
video_name = video_path.name

# 📝 قراءة الوصف من captions.json
captions = {}
captions_file = Path("captions.json")
if captions_file.exists():
    with open(captions_file, "r", encoding="utf-8") as f:
        captions = json.load(f)

caption = captions.get(video_name, "Enjoy this video! ✨ #reels")

# 🛰️ رفع الفيديو إلى Instagram Container
upload_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
params = {
    "media_type": "REELS",
    "video_url": video_url,
    "caption": caption,
    "access_token": access_token
}

response = requests.post(upload_url, data=params)
if response.status_code != 200:
    print("❌ فشل إنشاء Container:", response.text)
    exit(1)

creation_id = response.json().get("id")
print(f"✅ تم إنشاء Container: {creation_id}")

# 🛫 نشر الفيديو
publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
publish_params = {
    "creation_id": creation_id,
    "access_token": access_token
}

publish_response = requests.post(publish_url, data=publish_params)
if publish_response.status_code != 200:
    print("❌ فشل النشر:", publish_response.text)
    exit(1)

print("✅ تم النشر على Instagram.")

# 🧹 حذف الفيديو المحلي
video_path.unlink()
print(f"🗑️ تم حذف الفيديو من الجهاز: {video_path.name}")

# 🧹 حذف من Google Drive
if file_id:
    try:
        key_json = os.environ.get("SERVICE_ACCOUNT_KEY")
        if key_json:
            key_data = json.loads(key_json)
            credentials = service_account.Credentials.from_service_account_info(
                key_data, scopes=["https://www.googleapis.com/auth/drive"]
            )
            drive_service = build("drive", "v3", credentials=credentials)
            drive_service.files().delete(fileId=file_id).execute()
            print(f"🗑️ تم حذف الفيديو من Google Drive: {file_id}")
    except Exception as e:
        print(f"⚠️ خطأ أثناء حذف Google Drive: {e}")
