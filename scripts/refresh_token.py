import os
import requests

print("🔄 بدء تحديث التوكن...")

# جلب المتغيرات البيئية
refresh_token = os.environ.get("INSTAGRAM_REFRESH_TOKEN")
app_id = os.environ.get("META_APP_ID")
app_secret = os.environ.get("META_APP_SECRET")

# التحقق من القيم
if not refresh_token or not app_id or not app_secret:
    print("❌ تأكد من وجود المتغيرات: INSTAGRAM_REFRESH_TOKEN, META_APP_ID, META_APP_SECRET")
    exit(1)

# إرسال طلب لتحديث التوكن
url = "https://graph.facebook.com/v19.0/oauth/access_token"
params = {
    "grant_type": "fb_exchange_token",
    "client_id": app_id,
    "client_secret": app_secret,
    "fb_exchange_token": refresh_token
}

res = requests.get(url, params=params)
data = res.json()

# عرض النتيجة
if "access_token" in data:
    print("✅ تم تحديث التوكن بنجاح:")
    print(data["access_token"])  # يتم قراءته بواسطة GitHub Actions
else:
    print("❌ فشل تحديث التوكن:")
    print(data)
    exit(1)
