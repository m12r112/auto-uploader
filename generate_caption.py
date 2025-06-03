import os
import json
import openai
from pathlib import Path

# إعدادات عامة
OUTPUT_REELS_DIR = Path("output_reels")
CAPTIONS_OUTPUT_FILE = "captions.json"

# تأكد من وجود مجلد output_reels
OUTPUT_REELS_DIR.mkdir(exist_ok=True)

# تحميل API المجاني لـ GPT (في حال كنت تستخدم API مجاني خارجي)
openai.api_key = os.getenv("OPENAI_API_KEY", "your-free-api-key")

def detect_category_from_folder_name(folder_name):
    """استخلاص نوع الفيديو من اسم المجلد"""
    return folder_name.lower()

def generate_caption(prompt):
    """طلب توليد وصف من GPT بناءً على نوع الفيديو"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a social media expert. Generate short, engaging captions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens_
