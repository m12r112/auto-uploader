import os
import requests

# احصل على التوكن القديم من المتغير البيئي
old_token = os.environ.get("INSTAGRAM_OLD_TOKEN")

if not old_token:
    print("❌ لم يتم العثور على التوكن القديم في المتغير البيئي 'INSTAGRAM_OLD_TOKEN'.")
    exit(1)

# رابط تحديث التوكن من Meta API
url = "https://graph.instagram.com/refresh_access_token"

params = {
    "grant_type": "ig_refresh_token",
    "access_token": old_token
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    new_token = data.get("access_token")
    expires_in = data.get("expires_in")

    if new_token:
        print(f"{new_token}")  # ✅ يتم طباعته ليتم تمريره في GitHub Actions
    else:
        print("❌ لم يتم العثور على توكن جديد في الاستجابة.")
        exit(1)

except requests.exceptions.RequestException as e:
    print(f"❌ فشل الاتصال: {e}")
    exit(1)
