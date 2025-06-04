import requests
import os

# احصل على المتغيرات من بيئة GitHub
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
CURRENT_LONG_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")

# رابط طلب التحديث
url = "https://graph.facebook.com/v23.0/oauth/access_token"
params = {
    "grant_type": "fb_exchange_token",
    "client_id": APP_ID,
    "client_secret": APP_SECRET,
    "fb_exchange_token": CURRENT_LONG_TOKEN
}

response = requests.get(url, params=params)

if response.ok:
    new_token = response.json().get("access_token")
    print("✅ تم تحديث التوكن بنجاح")
    print("🔐 التوكن الجديد:", new_token)
    
    # حفظ التوكن الجديد في ملف لتتم قراءته لاحقًا من سكربتات النشر
    with open("latest_token.txt", "w") as f:
        f.write(new_token)
else:
    print("❌ فشل تحديث التوكن:", response.text)
