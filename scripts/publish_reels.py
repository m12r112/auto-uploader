import os
import requests

# قراءة المتغيرات البيئية
access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
ig_user_id = os.environ.get("IG_USER_ID")
fb_page_id = os.environ.get("FB_PAGE_ID")
video_url = os.environ.get("VIDEO_PUBLIC_URL")
file_id = os.environ.get("DRIVE_FILE_ID")

# ✅ طباعة القيم البيئية للتشخيص
print("📦 القيم البيئية:")
print("IG_USER_ID =", ig_user_id)
print("FB_PAGE_ID =", fb_page_id)
print("VIDEO_PUBLIC_URL =", video_url)
print("DRIVE_FILE_ID =", file_id)
print("ACCESS_TOKEN =", access_token[:10] + "..." if access_token else "❌ غير موجود")

# ✅ التحقق من وجود القيم الضرورية
if not ig_user_id or not fb_page_id or not video_url:
    print("❌ تأكد من IG_USER_ID و FB_PAGE_ID و VIDEO_PUBLIC_URL.")
    exit(1)

# ⏳ إنشاء منشور الفيديو عبر Instagram Graph API
url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
params = {
    "video_url": video_url,
    "caption": "Posted automatically 🎥",
    "access_token": access_token
}

res = requests.post(url, data=params)
response_data = res.json()

if "id" not in response_data:
    print("❌ فشل إنشاء container:", response_data)
    exit(1)

creation_id = response_data["id"]
print("📤 تم إنشاء container بنجاح، ID:", creation_id)

# 🚀 نشر الفيديو فعليًا
publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
publish_params = {
    "creation_id": creation_id,
    "access_token": access_token
}

publish_res = requests.post(publish_url, data=publish_params)
publish_data = publish_res.json()

if "id" in publish_data:
    print("✅ تم نشر الفيديو بنجاح على Instagram 🎉")
else:
    print("❌ فشل النشر:", publish_data)
