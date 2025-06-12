import os
import requests
from base64 import b64encode

# إعدادات GitHub
GITHUB_USERNAME = "your-username"
GITHUB_REPO = "your-repo-name"
GITHUB_BRANCH = "main"
GITHUB_FOLDER = "reels"  # اسم المجلد داخل المستودع
GITHUB_TOKEN = "ghp_your_personal_access_token"

# مجلد الفيديوهات الجاهزة
LOCAL_FOLDER = "final_reels"

def upload_file_to_github(file_path, filename):
    with open(file_path, "rb") as f:
        content = f.read()
    b64_content = b64encode(content).decode("utf-8")

    api_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FOLDER}/{filename}"

    payload = {
        "message": f"Upload {filename}",
        "content": b64_content,
        "branch": GITHUB_BRANCH
    }

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.put(api_url, json=payload, headers=headers)

    if response.status_code == 201:
        print(f"✅ تم رفع {filename} بنجاح.")
        return f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{GITHUB_BRANCH}/{GITHUB_FOLDER}/{filename}"
    elif response.status_code == 422:
        print(f"⚠️ الملف {filename} موجود بالفعل.")
        return f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{GITHUB_BRANCH}/{GITHUB_FOLDER}/{filename}"
    else:
        print(f"❌ فشل رفع {filename}: {response.status_code} {response.text}")
        return None

def main():
    if not os.path.exists(LOCAL_FOLDER):
        print("❌ مجلد final_reels غير موجود.")
        return

    for filename in os.listdir(LOCAL_FOLDER):
        if filename.endswith(".mp4"):
            file_path = os.path.join(LOCAL_FOLDER, filename)
            upload_file_to_github(file_path, filename)

if __name__ == "__main__":
    main()
