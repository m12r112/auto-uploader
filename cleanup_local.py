import shutil
from pathlib import Path

# المسارات التي نريد تنظيفها
TEMP_FOLDER = Path("temp_videos")
OUTPUT_FOLDER = Path("output_reels")

def clean_folder(folder):
    if folder.exists():
        for sub in folder.rglob("*.mp4"):
            try:
                sub.unlink()
                print(f"🗑️ Deleted: {sub}")
            except Exception as e:
                print(f"⚠️ Error deleting {sub}: {e}")

def main():
    print("🧹 Starting cleanup...")
    clean_folder(TEMP_FOLDER)
    clean_folder(OUTPUT_FOLDER)
    print("✅ Cleanup complete.")

if __name__ == "__main__":
    main()