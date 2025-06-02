
import os
import json
import random
from datetime import datetime
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips
from pathlib import Path

VIDEO_ROOT = "videos"
AUDIO_ROOT = "audio_library"
LOG_ROOT = "used_sounds_log"
OUTPUT_ROOT = "output_reels"

# تحميل الكلمات المفتاحية
with open("keywords.json") as f:
    keywords = json.load(f)["keywords"]

def get_unused_audio(keyword):
    audio_dir = Path(AUDIO_ROOT) / keyword
    used_log_file = Path(LOG_ROOT) / f"{keyword}.txt"
    used_sounds = set()
    if used_log_file.exists():
        with open(used_log_file, 'r') as f:
            used_sounds = set(line.strip() for line in f)
    all_sounds = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]
    unused_sounds = list(set(all_sounds) - used_sounds)
    if not unused_sounds:
        unused_sounds = all_sounds
        used_sounds = set()
    selected = random.choice(unused_sounds)
    with open(used_log_file, 'a') as f:
        if selected not in used_sounds:
            f.write(f"{selected}\n")
    return str(audio_dir / selected)

def match_audio_duration(audio_path, duration):
    original_audio = AudioFileClip(audio_path)
    if original_audio.duration > duration:
        return original_audio.subclip(0, duration)
    else:
        loops = int(duration // original_audio.duration)
        remainder = duration % original_audio.duration
        clips = [original_audio] * loops
        if remainder > 0:
            clips.append(original_audio.subclip(0, remainder))
        return concatenate_audioclips(clips)

def merge_audio_with_video(video_path, keyword, timestamp_label):
    video = VideoFileClip(video_path)
    audio_path = get_unused_audio(keyword)
    matched_audio = match_audio_duration(audio_path, video.duration)
    final = video.set_audio(matched_audio)
    today = datetime.now().strftime("%Y-%m-%d")
    out_name = f"{today}_{timestamp_label}.mp4"
    out_path = Path(OUTPUT_ROOT) / keyword
    out_path.mkdir(parents=True, exist_ok=True)
    final.write_videofile(str(out_path / out_name), codec="libx264", audio_codec="aac")
    return str(out_path / out_name)

def choose_random_short_video():
    random.shuffle(keywords)
    for keyword in keywords:
        video_dir = Path(VIDEO_ROOT) / keyword
        if video_dir.exists():
            all_videos = [f for f in os.listdir(video_dir) if f.endswith(".mp4")]
            short_videos = []
            for v in all_videos:
                try:
                    clip = VideoFileClip(str(video_dir / v))
                    if clip.duration <= 60:
                        short_videos.append((str(video_dir / v), keyword))
                except:
                    continue
            if short_videos:
                return random.choice(short_videos)
    return None, None

# تشغيل مهمّة الدمج اليومية
video1, kw1 = choose_random_short_video()
video2, kw2 = choose_random_short_video()

if video1:
    merge_audio_with_video(video1, kw1, "03PM")
if video2:
    merge_audio_with_video(video2, kw2, "09PM")
