import os
import requests

print("🔄 بدء تحديث التوكن...")

refresh_token = os.environ.get("INSTAGRAM_REFRESH_TOKEN")
app_id = os.environ.get("META_APP_ID")
app_secret = os.environ.get("META_APP_SECRET")

if not refresh_token or not app_id or not app_secret:
    print("❌ تأكد من وجود المتغيرات البيئية: INSTAGRAM_REFRESH_TOKEN و META_APP_ID و META_APP_SECRET.")
    exit(1)

url = f"https://graph.facebook.com/v19.0/oauth/access_token"
params = {
    "grant_type": "fb_exchange_token",
    "client_id": app_id,
    "client_secret": app_secret,
    "fb_exchange_token": refresh_token
}

res = requests.get(url, params=params)
data = res.json()

if "access_token" in data:
    print("✅ تم الحصول على التوكن الجديد:")
    print(data["access_token"])  # يتم تمريره لـ GitHub Actions
else:
    print("❌ فشل التحديث:")
    print(data)
    exit(1)
