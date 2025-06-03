import os
import json
import random
import requests
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# 1) إعداد مجلد محلي لحفظ الفيديوهات
VIDEO_ROOT = Path("videos")
VIDEO_ROOT.mkdir(exist_ok=True)

# 2) تحميل الكلمات المفتاحية
with open("keywords.json") as f:
    keywords = json.load(f)["keywords"]

# 3) اختيار كلمتين عشوائيتين
selected_keywords = random.sample(keywords, k=2)

# 4) قراءة مفتاح Pexels من environment
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
if not PEXELS_API_KEY:
    # بدلًا من رفع استثناء قاتل، نطبع تحذير ونستمر (حتى لو لم نجد مفتاح)
    print("⚠️ WARNING: PEXELS_API_KEY not found in env. Skipping Pexels API.")
else:
    print(f"🔐 PEXELS_API_KEY found (starts with): {PEXELS_API_KEY[:6]}...")

# 5) معرّف مجلد Google Drive
DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")
if not DRIVE_FOLDER_ID:
    raise Exception("❌ DRIVE_FOLDER_ID not found.")

# 6) رابط البحث في Pexels
PEXELS_API_URL = "https://api.pexels.com/videos/search"
headers = {"Authorization": PEXELS_API_KEY} if PEXELS_API_KEY else {}

def fetch_video_url(keyword):
    """
    محاولة جلب فيديو من Pexels؛ 
    إذا لم يوجد PEXELS_API_KEY، نعيد None لنتيح لسكربت الرفع أن يأخذ رابط ثابت أو يتخطّى.
    """
    if not PEXELS_API_KEY:
        return None

    print(f"🔍 [Pexels] Searching for '{keyword}'...")
    params = {"query": keyword, "per_page": 20}
    try:
        response = requests.get(PEXELS_API_URL, headers=headers, params=params, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error calling Pexels API: {e}")
        return None

    data = response.json()
    candidates = []
    for video in data.get("videos", []):
        for file in video.get("video_files", []):
            width = file.get("width")
            height = file.get("height")
            # نختار الفيديو العمودي 720p+
            if width and height and height > width and height >= 720:
                candidates.append(file["link"])
    if candidates:
        selected = random.choice(candidates)
        print(f"🔗 Selected vertical video: {selected}")
        return selected

    print(f"❌ No vertical video found for keyword: {keyword}")
    return None

def download_video(url, save_path):
    """
    نحاول تنزيل الفيديو من أي رابط (Pexels أو Vimeo أو غيره).
    """
    print(f"⬇️ Downloading to {save_path} ...")
    try:
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Downloaded: {save_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False

def get_or_create_folder(drive_service, parent_id, folder_name):
    """
    تأكد من وجود المجلد الفرعي داخل Drive؛ إذا لم يكن موجودًا، أنشئه.
    """
    query = (
        f"mimeType='application/vnd.google-apps.folder' "
        f"and name='{folder_name}' "
        f"and '{parent_id}' in parents "
        f"and trashed=false"
    )
    results = drive_service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)"
    ).execute()
    items = results.get("files", [])
    if items:
        return items[0]["id"]

    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id]
    }
    folder = drive_service.files().create(body=file_metadata, fields="id").execute()
    return folder.get("id")

def upload_to_drive(local_file_path, parent_folder_id, keyword):
    """
    يرفع الفيديو إلى Google Drive داخل هيكل:
    AutoUploader / Videos / {keyword} / {filename}
    """
    print(f"☁️ Uploading '{local_file_path}' under keyword '{keyword}' ...")
    try:
        creds = service_account.Credentials.from_service_account_file(
            "service_account.key",
            scopes=["https://www.googleapis.com/auth/drive"]
        )
    except Exception as e:
        print(f"❌ Couldn't load service_account.key: {e}")
        return

    drive_service = build("drive", "v3", credentials=creds)

    try:
        videos_root_id = get_or_create_folder(drive_service, parent_folder_id, "Videos")
        keyword_folder_id = get_or_create_folder(drive_service, videos_root_id, keyword)
    except HttpError as e:
        print(f"❌ Error creating/fetching folder: {e}")
        return

    file_metadata = {
        "name": os.path.basename(local_file_path),
        "parents": [keyword_folder_id]
    }
    media = MediaFileUpload(local_file_path, mimetype="video/mp4")
    try:
        uploaded = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, name"
        ).execute()
        print(f"✅ Uploaded to Drive: {uploaded['name']} (ID: {uploaded['id']}) in '{keyword}'")
    except HttpError as e:
        print(f"❌ Error uploading file: {e}")

def main():
    print(f"📁 Parent Drive folder ID = {DRIVE_FOLDER_ID}")
    for keyword in selected_keywords:
        print(f"\n🔍 Searching for: {keyword}")
        video_url = fetch_video_url(keyword)

        # إذا لم يُوجد PEXELS_API_KEY أو لم يجد فيديو من Pexels، يمكنك استبدال “video_url”
        # برابط ثابت أو تجربة كلمة أخرى. للتجربة الآن فقط نطبع رسالة:
        if not video_url:
            print(f"⚠️ Using fallback static URL for '{keyword}'.")
            # مثال: رابط Vimeo ثابت للعرض (يمكنك تغييره لأي رابط صالح)
            video_url = "https://player.vimeo.com/external/411138813.sd.mp4?s=...

        # الآن نحمّل الفيديو من الرابط (سواء من Pexels أو من الرابط الثابت)
        filename = f"{keyword}_{random.randint(1000,9999)}.mp4"
        keyword_dir = VIDEO_ROOT / keyword
        keyword_dir.mkdir(parents=True, exist_ok=True)
        save_path = keyword_dir / filename

        if download_video(video_url, save_path):
            upload_to_drive(str(save_path), DRIVE_FOLDER_ID, keyword)

if __name__ == "__main__":
    main()
