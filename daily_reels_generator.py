import os
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip
from docx import Document
from datetime import datetime
import shutil

VIDEOS_DIR = Path("videos")
AUDIO_DIR = Path("audio_library")
OUTPUT_DIR = Path("output_reels")
LOG_FILE = Path("Published_Videos_Log.docx")

OUTPUT_DIR.mkdir(exist_ok=True)

def log_video(keyword, filename):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    if LOG_FILE.exists():
        doc = Document(LOG_FILE)
    else:
        doc = Document()
        doc.add_heading("Published Videos Log", 0)
        table = doc.add_table(rows=1, cols=3)
        hdr = table.rows[0].cells
        hdr[0].text = "Date"
        hdr[1].text = "Keyword"
        hdr[2].text = "Filename"

    table = doc.tables[0]
    row = table.add_row().cells
    row[0].text = now
    row[1].text = keyword
    row[2].text = filename

    doc.save(LOG_FILE)

def process_video(video_path: Path, keyword: str):
    print(f"🎬 Processing {video_path.name}")
    output_path = OUTPUT_DIR / video_path.name

    try:
        clip = VideoFileClip(str(video_path))
        if clip.audio is not None:
            # الفيديو يحتوي على صوت → يُنقل كما هو
            shutil.copy(str(video_path), str(output_path))
            print(f"🔊 Video has audio, copied directly: {output_path.name}")
        else:
            # الفيديو صامت → دمجه مع الصوت
            audio_file = AUDIO_DIR / f"{keyword}.mp3"
            if not audio_file.exists():
                print(f"❌ Audio not found for {keyword}, skipping...")
                return

            audio = AudioFileClip(str(audio_file)).subclip(0, clip.duration)
            clip = clip.set_audio(audio)
            clip.write_videofile(str(output_path), codec="libx264", audio_codec="aac")
            print(f"🔇 Video was silent, merged with audio: {output_path.name}")

        log_video(keyword, output_path.name)
    except Exception as e:
        print(f"❌ Error processing {video_path.name}: {e}")

def main():
    for keyword_folder in VIDEOS_DIR.iterdir():
        if keyword_folder.is_dir():
            keyword = keyword_folder.name
            for video_file in keyword_folder.glob("*.mp4"):
                process_video(video_file, keyword)

if __name__ == "__main__":
    main()
