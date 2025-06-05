import os
import requests

# متغيرات البيئة
APP_ID = os.environ["META_APP_ID"]
APP_SECRET = os.environ["META_APP_SECRET"]
REFRESH_TOKEN = os.environ["INSTAGRAM_REFRESH_TOKEN"]

# رابط تحديث التوكن
url = (
    f"https://graph.instagram.com/refresh_access_token"
    f"?grant_type=ig_refresh_token"
    f"&access_token={REFRESH_TOKEN}"
)

# طلب التحديث
response = requests.get(url)
data = response.json()

# عرض النتيجة
if "access_token" in data:
    new_token = data["access_token"]
    print("✅ NEW_INSTAGRAM_ACCESS_TOKEN=" + new_token)
else:
    print("❌ فشل التحديث:", data)
    exit(1)
