name: Daily Automation

on:
  schedule:
    - cron: '0 5 * * *'  # يوميًا الساعة 5:00 صباحًا بتوقيت بغداد
  workflow_dispatch:

jobs:
  auto-run:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Fetch videos and audio
        run: python daily_fetch_and_upload.py
        env:
          SERVICE_ACCOUNT_KEY: ${{ secrets.SERVICE_ACCOUNT_KEY }}

      - name: Generate Reels
        run: python daily_reels_generator.py

      - name: Generate Captions using GPT4Free
        run: python generate_caption.py

      - name: Upload to Google Drive
        run: python upload_to_drive.py
        env:
          SERVICE_ACCOUNT_KEY: ${{ secrets.SERVICE_ACCOUNT_KEY }}

      - name: Send weekly report
        run: python send_weekly_report.py
        env:
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}

      - name: Clean up local videos
        run: python cleanup_local.py
