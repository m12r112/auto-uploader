import os
import requests
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ✅ طباعة القيم البيئية للتشخيص
ig_user_id = os.environ.get("IG_USER_ID")
fb_page_id = os.environ.get("FB_PAGE_ID")
access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
video_url = os.environ.get("VIDEO_PUBLIC_URL")
drive_file_id = os.environ.get("DRIVE_FILE_ID")

print("📦 القيم البيئية:")
print("IG_USER_ID =", ig_user_id)
print("FB_PAGE_ID =", fb_page_id)
print("VIDEO_PUBLIC_URL =", video_url)
print("DRIVE_FILE_ID =", drive_file_id)

# ✅ التحقق من وجود القيم الضرورية
if not ig_user_id or not fb_page_id or not video_url:
    print("❌ تأكد من IG_USER_ID و FB_PAGE_ID و VIDEO_PUBLIC_URL.")
    exit(1)

# ✅ إنشاء container للفيديو
container_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
container_payload = {
    "video_url": video_url,
    "media_type": "REELS",
    "caption": "🎬 Enjoy the moment! #relaxing #nature #reels",
    "access_token": access_token
}
container_res = requests.post(container_url, data=container_payload)
container_data = container_res.json()

if "id" not in container_data:
    print("❌ فشل إنشاء الـ container:", container_data)
    exit(1)

creation_id = container_data["id"]
print("📤 تم إنشاء Container بنجاح:", creation_id)

# ✅ نشر الفيديو
publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
publish_payload = {
    "creation_id": creation_id,
    "access_token": access_token
}
publish_res = requests.post(publish_url, data=publish_payload)
publish_data = publish_res.json()

if "id" not in publish_data:
    print("❌ فشل النشر:", publish_data)
    exit(1)

print("✅ تم نشر الريلز بنجاح:", publish_data["id"])

# ✅ حذف الفيديو من
