import os
from pathlib import Path
from openai import OpenAI

# إعداد عميل OpenAI باستخدام المفتاح الموجود في المتغير البيئي
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# المسارات
OUTPUT_REELS_DIR = Path("output_reels")
CAPTIONS_DIR = Path("captions")

# قالب الطلب
PROMPT_TEMPLATE = (
    "Generate a deep, emotionally resonant caption in English for an Instagram Reel about '{keyword}'. "
    "The caption should subtly influence the subconscious, evoke emotion, and encourage engagement "
    "(like, comment, follow) without being too obvious. Do not use hashtags. Keep it under 50 words."
)

# توليد الوصف من GPT
def generate_caption(keyword):
    prompt = PROMPT_TEMPLATE.format(keyword=keyword)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=100
    )
    return response.choices[0].message.content.strip()

# معالجة جميع الفيديوهات تلقائيًا من المجلدات الفرعية
def process_all_videos():
    for keyword_folder in OUTPUT_REELS_DIR.iterdir():
        if not keyword_folder.is_dir():
            continue

        keyword = keyword_folder.name
        for video_file in keyword_folder.glob("*.mp4"):
            video_name = video_file.name
            caption = generate_caption(keyword)

            # حفظ الوصف في مجلد captions/keyword/
            out_dir = CAPTIONS_DIR / keyword
            out_dir.mkdir(parents=True, exist_ok=True)
            txt_path = out_dir / (Path(video_name).stem + ".txt")

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(caption)

            print(f"✅ Caption saved: {txt_path}")

# نقطة البداية
if __name__ == "__main__":
    process_all_videos()
