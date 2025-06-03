import os
import json
import random
import requests
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# ─────────────────────────────────────────────
# 1) مجلد التخزين المحلي للفيديوهات
# ─────────────────────────────────────────────
VIDEO_ROOT = Path("videos")
VIDEO_ROOT.mkdir(exist_ok=True)

# ─────────────────────────────────────────────
# 2) تحميل الكلمات المفتاحية واختيار كلمتين عشوائيتين
# ─────────────────────────────────────────────
with open("keywords.json", encoding="utf-8") as f:
    keywords = json.load(f)["keywords"]
selected_keywords = random.sample(keywords, k=2)

# ─────────────────────────────────────────────
# 3) مفاتيح البيئة الأساسية
# ─────────────────────────────────────────────
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
print(
    f"🔐 DEBUG: PEXELS_API_KEY begins with: {PEXELS_API_KEY[:6]}..."
    if PEXELS_API_KEY else
    "❌ PEXELS_API_KEY not found in env"
)
if not PEXELS_API_KEY:
    raise Exception("❌ PEXELS_API_KEY not found in environment.")

DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")
if not DRIVE_FOLDER_ID:
    raise Exception("❌ DRIVE_FOLDER_ID not found in environment.")

# ─────────────────────────────────────────────
# 4) إعداد Pexels API
# ─────────────────────────────────────────────
PEXELS_API_URL = "https://api.pexels.com/videos/search"
headers = {"Authorization": PEXELS_API_KEY}

def fetch_video_url(keyword: str) -> str | None:
    """جلب رابط فيديو عمودي من Pexels، أو إرجاع None إذا لم يُعثر عليه."""
    print(f"🔍 [Pexels] Searching for '{keyword}' …")
    params = {"query": keyword, "per_page": 20}
    try:
        resp = requests.get(PEXELS_API_URL, headers=headers, params=params, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ Pexels API error: {e}")
        return None

    data = resp.json()
    candidates: list[str] = []
    for video in data.get("videos", []):
        for file in video.get("video_files", []):
            w, h = file.get("width"), file.get("height")
            # شرط عمودي ≥ 720p
            if w and h and h > w and h >= 720:
                candidates.append(file["link"])

    if candidates:
        chosen = random.choice(candidates)
        print(f"🔗 Selected vertical video: {chosen}")
        return chosen

    print(f"❌ No vertical video found for '{keyword}'")
    return None

def download_video(url: str, save_path: Path) -> bool:
    """تنزيل الفيديو إلى المسار المحدد."""
    print(f"⬇️ Downloading → {save_path}")
    try:
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Saved: {save_path.name}")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

# ─────────────────────────────────────────────
# 5) أدوات Google Drive
# ─────────────────────────────────────────────
def get_or_create_folder(service, parent_id: str, name: str) -> str:
    query = (
        f"mimeType='application/vnd.google-apps.folder' "
        f"and name='{name}' and '{parent_id}' in parents and trashed=false"
    )
    res = service.files().list(q=query, spaces="drive", fields="files(id,name)").execute()
    if res.get("files"):
        return res["files"][0]["id"]

    meta = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    created = service.files().create(body=meta, fields="id").execute()
    return created["id"]

def upload_to_drive(local_path: Path, parent_id: str, keyword: str) -> None:
    """رفع الملف إلى Google Drive داخل المسار المناسب."""
    creds = service_account.Credentials.from_service_account_file(
        "service_account.key",
        scopes=["https://www.googleapis.com/auth/drive"],
    )
    service = build("drive", "v3", credentials=creds)

    try:
        videos_root = get_or_create_folder(service, parent_id, "Videos")
        keyword_folder = get_or_create_folder(service, videos_root, keyword)
    except HttpError as e:
        print(f"❌ Folder creation error: {e}")
        return

    meta = {"name": local_path.name, "parents": [keyword_folder]}
    media = MediaFileUpload(local_path, mimetype="video/mp4")
    try:
        uploaded = service.files().create(body=meta, media_body=media, fields="id").execute()
        print(f"✅ Uploaded to Drive (ID={uploaded['id']}) → Videos/{keyword}/{local_path.name}")
    except HttpError as e:
        print(f"❌ Upload error: {e}")

# ─────────────────────────────────────────────
# 6) الحلقة الرئيسية
# ─────────────────────────────────────────────
def main() -> None:
    print(f"📂 Parent Drive folder ID = {DRIVE_FOLDER_ID}")
    for keyword in selected_keywords:
        print(f"\n🔍 Keyword: {keyword}")
        url = fetch_video_url(keyword)
        if not url:
            continue

        keyword_dir = VIDEO_ROOT / keyword
        keyword_dir.mkdir(parents=True, exist_ok=True)
        fname = f"{keyword}_{random.randint(1000,9999)}.mp4"
        save_to = keyword_dir / fname

        if download_video(url, save_to):
            upload_to_drive(save_to, DRIVE_FOLDER_ID, keyword)

if __name__ == "__main__":
    main()
