import os

folders = [
    "videos",
    "audio_library",
    "final_reels"
]

def create_folder_if_missing(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"✅ تم إنشاء المجلد: {folder}")
    else:
        print(f"📁 المجلد موجود مسبقًا: {folder}")

def main():
    for folder in folders:
        create_folder_if_missing(folder)

if __name__ == "__main__":
    main()
