import os
from pathlib import Path

# المجلدات
TEMP_FOLDER = Path("temp_videos")
OUTPUT_FOLDER = Path("output_reels")
LOG_FILE = Path("Published_Videos_Log.txt")

def clean_folder(folder, uploaded_names=None):
    if folder.exists():
        for sub in folder.rglob("*.mp4"):
            if uploaded_names is None or sub.name in uploaded_names:
                try:
                    sub.unlink()
                    print(f"🗑️ Deleted: {sub}")
                except Exception as e:
                    print(f"⚠️ Error deleting {sub}: {e}")

def read_uploaded_log():
    if LOG_FILE.exists():
        with open(LOG_FILE, "r") as f:
            return set(line.strip() for line in f)
    return set()

def main():
    print("🧹 Starting smart cleanup...")
    uploaded_files = read_uploaded_log()
    
    # نحذف جميع ملفات temp_videos
    clean_folder(TEMP_FOLDER)

    # نحذف فقط الفيديوهات التي تم رفعها
    clean_folder(OUTPUT_FOLDER, uploaded_files)

    print("✅ Smart cleanup complete.")

if __name__ == "__main__":
    main()
