import os
import requests
import json
from pathlib import Path

# 🔑 تحميل التوكن من البيئة
access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
if not access_token:
    print("❌ لم يتم العثور على التوكن، لا يمكن النشر.")
    exit(1)

# إعدادات Instagram
page_id = os.environ.get("FB_PAGE_ID")      # معرف الصفحة
ig_user_id = os.environ.get("IG_USER_ID")   # معرف حساب إنستغرام المرتبط

if not page_id or not ig_user_id:
    print("❌ يجب توفير IG_USER_ID و FB_PAGE_ID في المتغيرات البيئية.")
    exit(1)

# 📁 مجلد الفيديوهات الجاهزة
reels_folder = Path("final_reels")
video_files = list(reels_folder.glob("*.mp4"))

if not video_files:
    print("❌ لا توجد فيديوهات في final_reels/")
    exit(0)

# 🧾 تحميل ملف الأوصاف
captions = {}
captions_file = Path("captions.json")
if captions_file.exists():
    with open(captions_file, "r", encoding="utf-8") as f:
        captions = json.load(f)

# 🖼️ اختر أول فيديو جاهز للنشر
video_path = video_files[0]
video_name = video_path.name

# 📝 استخرج الوصف المناسب
caption = captions.get(video_name, "Enjoy this video! ✨ #reels")

# 🧭 هنا يجب أن نستخدم رابط مباشر للفيديو (Google Drive أو غيره)
# سنفترض أن الرابط تم رفعه يدوياً أو من سكربت خارجي
video_public_url = os.environ.get("VIDEO_PUBLIC_URL")  # هذا يجب أن يتم تمريره من workflow

if not video_public_url:
    print("❌ لم يتم تحديد رابط مباشر للفيديو (VIDEO_PUBLIC_URL).")
    exit(1)

# 🛰️ إنشاء Instagram Media Container
upload_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
params = {
    "media_type": "REELS",
    "video_url": video_public_url,
    "caption": caption,
    "access_token": access_token
}

response = requests.post(upload_url, data=params)
if response.status_code != 200:
    print("❌ فشل في إنشاء Media Container:", response.text)
    exit(1)

creation_id = response.json().get("id")
print(f"✅ تم إنشاء Container بنجاح: {creation_id}")

# 🛫 نشر الفيديو بعد إنشائه
publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
publish_params = {
    "creation_id": creation_id,
    "access_token": access_token
}

publish_response = requests.post(publish_url, data=publish_params)
if publish_response.status_code != 200:
    print("❌ فشل في نشر الفيديو:", publish_response.text)
    exit(1)

print("✅ تم نشر الفيديو بنجاح على Instagram Reels!")
