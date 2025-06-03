import os
import shutil
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips

# المسارات
VIDEOS_DIR = Path("videos")
AUDIO_DIR = Path("audio_library")
OUTPUT_DIR = Path("output_reels")

OUTPUT_DIR.mkdir(exist_ok=True)

def has_audio(video_path):
    """يتحقق إذا كان الفيديو يحتوي على صوت"""
    try:
        clip = VideoFileClip(str(video_path))
        return clip.audio is not None
    except:
        return False

def get_matching_audio(audio_folder, duration):
    """يبحث عن ملف صوتي من نفس النوع ويطابق المدة"""
    for audio_file in Path(audio_folder).glob("*.mp3"):
        audio_clip = AudioFileClip(str(audio_file))
        if abs(audio_clip.duration - duration) < 1:
            return audio_clip
    return None

def process_video(video_path, keyword):
    filename = video_path.name
    out_path = OUTPUT_DIR / filename

    if has_audio(video_path):
        shutil.copy(video_path, out_path)
        print(f"📁 تم نسخ: {filename} (يحتوي على صوت)")
    else:
        clip = VideoFileClip(str(video_path))
        audio_folder = AUDIO_DIR / keyword
        audio_clip = get_matching_audio(audio_folder, clip.duration)

        if audio_clip:
            clip = clip.set_audio(audio_clip)
            clip.write_videofile(str(out_path), codec="libx264", audio_codec="aac")
            print(f"🔊 تم الدمج: {filename} + صوت من {audio_folder.name}")
        else:
            print(f"❌ لم يتم العثور على صوت مطابق لـ: {filename}")

def main():
    for keyword_dir in VIDEOS_DIR.iterdir():
        if keyword_dir.is_dir():
            keyword = keyword_dir.name
            for video_file in keyword_dir.glob("*.mp4"):
                process_video(video_file, keyword)

if __name__ == "__main__":
    main()
