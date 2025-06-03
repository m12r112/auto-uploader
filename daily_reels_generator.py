# ✅ daily_reels_generator.py (مُعدّل)

import os
import random
import shutil
from pathlib import Path
from moviepy.editor import VideoFileClip
from docx import Document

# 📁 مجلدات الإدخال والإخراج
VIDEOS_DIR = Path("videos")
OUTPUT_DIR = Path("output_reels")
LOG_FILE = Path("Published_Videos_Log.docx")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 📄 تحميل سجل الفيديوهات
if LOG_FILE.exists():
    doc = Document(LOG_FILE)
else:
    doc = Document()
    doc.add_heading("Published Videos Log", 0)

used_videos = set(p.text for p in doc.paragraphs[1:] if p.text)

# 🔍 العثور على فيديوهات جديدة تحتوي على صوت فقط
available_videos = []
for subfolder in VIDEOS_DIR.glob("*/"):
    for video_file in subfolder.glob("*.mp4"):
        if video_file.name in used_videos:
            continue
        try:
            clip = VideoFileClip(str(video_file))
            if clip.audio is not None:
                available_videos.append(video_file)
        except Exception as e:
            print(f"⚠️ خطأ عند فحص {video_file.name}: {e}")

# 🎯 اختيار 2 فيديو عشوائي فقط
selected = random.sample(available_videos, k=min(2, len(available_videos)))

for video_path in selected:
    dest_path = OUTPUT_DIR / video_path.name
    shutil.copy(video_path, dest_path)
    print(f"✅ تم النسخ: {video_path.name}")
    doc.add_paragraph(video_path.name)

# 💾 حفظ السجل
doc.save(LOG_FILE)
print("📄 تم تحديث سجل الفيديوهات.")
