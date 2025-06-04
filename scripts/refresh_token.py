from pathlib import Path
import os
import requests

# استيراد المتغيرات من بيئة GitHub Actions
APP_ID = os.getenv("FB_APP_ID")
APP_SECRET = os.getenv("FB_APP_SECRET")
CURRENT_LONG_TOKEN = os.getenv("FB_ACCESS_TOKEN")

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
    
    # حفظ التوكن الجديد في ملف
    with open("latest_token.txt", "w") as f:
        f.write(new_token)
else:
    print("❌ فشل تحديث التوكن:", response.text)
