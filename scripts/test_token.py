import os
import requests

access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")

print("🔑 Access Token:", access_token[:10] + "..." if access_token else "❌ غير موجود")

url = f"https://graph.facebook.com/v19.0/me?access_token={access_token}"
response = requests.get(url)
data = response.json()

print("📡 نتيجة الاختبار:")
print(data)
