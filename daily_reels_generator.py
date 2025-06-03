import os
import shutil
import random
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips
from pydub import AudioSegment

# المسارات
VIDEOS_DIR = Path("videos")
AUDIO_DIR = Path("audio_library")
OUTPUT_DIR = Path("output_reels")
USED_AUDIO_LOG = Path("used_audio.json")

import json
OUTPUT_DIR.mkdir(exist_ok=True)

# تحميل السجل إذا وُجد
if USED_AUDIO_LOG.exists():
    with open(USED_AUDIO_LOG, "r") as f:
        used_audio = json.load(f)
else:
    used_audio = {}

def has_audio(video_path):
    try:
        clip = VideoFileClip(str(video_path))
        return clip.audio is not None
    except:
        return False

def get_random_audio(audio_folder, keyword, duration):
    all_audio_files = list(Path(audio_folder).glob("*.mp3"))
    if not all_audio_files:
        return None

    used = set(used_audio.get(keyword, []))
    unused = [f for f in all_audio_files if f.name not in used]

    if not unused:
        unused = all_audio_files
        used = set()  # نبدأ من جديد إذا استُهلكت كل الملفات

    selected = random.choice(unused)
    used.add(selected.name)
    used_audio[keyword] = list(used)

    # معالجة الطول باستخدام pydub
    sound = AudioSegment.from_file(selected)
    video_duration_ms = int(duration * 1000)

    if len(sound) > video_duration_ms:
        sound = sound[:video_duration_ms]
    else:
        # تكرار الصوت ليصل للطول المطلوب
        repeats = (video_duration_ms // len(sound)) + 1
        sound = (sound * repeats)[:video_duration_ms]

    temp_audio_path = f"temp_audio_{keyword}.mp3"
    sound.export(temp_audio_path, format="mp3")
    return temp_audio_path

def process_video(video_path, keyword):
    filename = video_path.name
    out_path = OUTPUT_DIR / filename

    if has_audio(video_path):
        shutil.copy(video_path, out_path)
        print(f"📁 تم نسخ: {filename} (يحتوي على صوت)")
    else:
        clip = VideoFileClip(str(video_path))
        audio_folder = AUDIO_DIR / keyword
        audio_path = get_random_audio(audio_folder, keyword, clip.duration)

        if audio_path and Path(audio_path).exists():
            audio_clip = AudioFileClip(audio_path)
            clip = clip.set_audio(audio_clip)
            clip.write_videofile(str(out_path), codec="libx264", audio_codec="aac", verbose=False, logger=None)
            print(f"🔊 تم الدمج: {filename} + صوت من {audio_folder.name}")
            os.remove(audio_path)  # حذف الصوت المؤقت
        else:
            print(f"❌ لا يوجد صوت مناسب لـ: {filename}")

def main():
    for keyword_dir in VIDEOS_DIR.iterdir():
        if keyword_dir.is_dir():
            keyword = keyword_dir.name
            for video_file in keyword_dir.glob("*.mp4"):
                process_video(video_file, keyword)

    # حفظ السجل بعد كل تشغيل
    with open(USED_AUDIO_LOG, "w") as f:
        json.dump(used_audio, f)

if __name__ == "__main__":
    main()
