import os
import random
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
from docx import Document
from datetime import datetime
import shutil

VIDEOS_DIR = Path("videos")
AUDIO_DIR = Path("audio_library")
OUTPUT_DIR = Path("final_reels")
LOG_FILE = Path("Published_Videos_Log.docx")

OUTPUT_DIR.mkdir(exist_ok=True)
if not LOG_FILE.exists():
    doc = Document()
    doc.add_heading("Published Videos Log", 0)
    doc.save(LOG_FILE)

def is_video_with_audio(path):
    try:
        clip = VideoFileClip(str(path))
        has_audio = clip.audio is not None
        clip.close()
        return has_audio
    except:
        return False

def select_unused_audio(audio_folder, used_list):
    all_audio = list(audio_folder.glob("*.mp3"))
    unused = [a for a in all_audio if a.name not in used_list]
    if not unused:
        used_list.clear()
        unused = all_audio
    return random.choice(unused) if unused else None

def load_used_audios(log_path):
    if not log_path.exists():
        return set()
    doc = Document(log_path)
    return {p.text.split(" | ")[-1] for p in doc.paragraphs if "Audio:" in p.text}

def log_video(filename, audio_name):
    doc = Document(LOG_FILE)
    doc.add_paragraph(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Video: {filename} | Audio: {audio_name}")
    doc.save(LOG_FILE)

def process_videos():
    used_audios = load_used_audios(LOG_FILE)
    processed_count = 0

    for keyword_folder in VIDEOS_DIR.iterdir():
        if not keyword_folder.is_dir():
            continue

        videos = list(keyword_folder.glob("*.mp4"))
        random.shuffle(videos)

        for video_path in videos:
            if processed_count >= 2:
                return

            has_audio = is_video_with_audio(video_path)

            if has_audio:
                shutil.copy(video_path, OUTPUT_DIR / video_path.name)
                log_video(video_path.name, "original_audio")
                processed_count += 1
            else:
                audio_folder = AUDIO_DIR / keyword_folder.name
                selected_audio = select_unused_audio(audio_folder, used_audios)

                if not selected_audio:
                    print(f"❌ لا يوجد صوت متاح لـ {keyword_folder.name}")
                    continue

                video = VideoFileClip(str(video_path))
                audio = AudioFileClip(str(selected_audio))

                # قص أو تكرار الصوت لمطابقة طول الفيديو
                if audio.duration >= video.duration:
                    audio = audio.subclip(0, video.duration)
                else:
                    loop_count = int(video.duration // audio.duration) + 1
                    audio = CompositeAudioClip([audio] * loop_count).subclip(0, video.duration)

                final_video = video.set_audio(audio)
                output_path = OUTPUT_DIR / video_path.name
                final_video.write_videofile(str(output_path), codec="libx264", audio_codec="aac", verbose=False, logger=None)

                video.close()
                audio.close()
                final_video.close()

                log_video(video_path.name, selected_audio.name)
                processed_count += 1

if __name__ == "__main__":
    process_videos()
