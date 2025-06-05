import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# إعداد المفتاح
key_json = os.environ["SERVICE_ACCOUNT_KEY"]
with open("service_account.key", "w") as f:
    f.write(key_json)

credentials = service_account.Credentials.from_service_account_file(
    "service_account.key",
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

# البحث عن AutoUploader
def find_folder(name, parent=None):
    q = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
    if parent:
        q += f" and '{parent}' in parents"
    else:
        q += " and 'root' in parents"
    results = drive_service.files().list(q=q, fields="files(id, name)").execute()
    folders = results.get("files", [])
    return folders[0]["id"] if folders else None

main_folder_id = find_folder("AutoUploader")

if not main_folder_id:
    print("❌ لم يتم العثور على مجلد AutoUploader")
    exit(1)

# طباعة المجلدات الفرعية
subfolders = drive_service.files().list(
    q=f"'{main_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'",
    fields="files(id, name)"
).execute().get("files", [])

print("📂 المجلدات الموجودة داخل AutoUploader:")
for folder in subfolders:
    print("-", folder["name"])
