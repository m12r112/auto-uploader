
import os
import openai
import json
from pathlib import Path

# تحميل المفتاح من متغير البيئة (GitHub Secrets)
openai.api_key = os.environ["OPENAI_API_KEY"]

CAPTIONS_DIR = "captions"
VIDEO_INFO = [
    {"name": "2025-06-03_03PM.mp4", "keyword": "rain"},
    {"name": "2025-06-03_09PM.mp4", "keyword": "fire"}
]

PROMPT_TEMPLATE = (
    "Generate a deep, emotionally resonant caption in English for an Instagram Reel about '{keyword}'. "
    "The caption should subtly influence the subconscious, evoke emotion, and encourage engagement "
    "(like, comment, follow) without being too obvious. Do not use hashtags. Keep it under 50 words."
)

def generate_caption(keyword):
    prompt = PROMPT_TEMPLATE.format(keyword=keyword)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=100
    )
    return response["choices"][0]["message"]["content"].strip()

def save_caption(video_name, text):
    os.makedirs(CAPTIONS_DIR, exist_ok=True)
    txt_path = Path(CAPTIONS_DIR) / (Path(video_name).stem + ".txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"📝 Caption saved: {txt_path}")

def main():
    for video in VIDEO_INFO:
        caption = generate_caption(video["keyword"])
        save_caption(video["name"], caption)

if __name__ == "__main__":
    main()
