# Telegram YouTube to Audio Converter Bot

This Telegram bot allows users to convert YouTube video links into audio files and send them to the user. It also has the capability to split videos into fragments based on timestamps and send them.

## Features

- Convert YouTube video links into audio files.
- Send audio files to users.
- Split videos into fragments based on timestamps and send them.

## Getting Started

To get started with this bot, follow these steps:

1. Start a chat with the bot.
2. Send a YouTube video link.
3. Specify whether you want to convert the entire video to audio or split it into fragments.
4. Enjoy your audio content!

## Technologies Used

This bot was developed using the following technologies:

- `imageio-ffmpeg` v0.4.8
- `moviepy` v1.0.3
- `pyTelegramBotAPI` v3.7.1
- `pytube` v15.0.0
- `SQLAlchemy` v2.0.20

Please note that development of this bot is currently on hold, but during the development, the following issues have been identified:

1. **Problem with Description Retrieval:**
   - In `venv/lib/python3.10/site-packages/pytube/cipher.py` on line 411:
     - Old: `transform_plan_raw = find_object_from_startpoint(raw_code, match.span()[1] - 1)`
     - New: `transform_plan_raw = js`

   - In `venv/lib/python3.10/site-packages/pytube/parser.py` on line 159:
     - Old: `func_regex = re.compile(r"function\([^)]*\)") - probably
     - New: `func_regex = re.compile(r"function\([^)]?\)"`

2. **Problem with Video Access:**
   - In `venv/lib/python3.10/site-packages/pytube/innertube.py` on line 223:
     - Old: `def __init__(self, client='ANDROID_MUSIC', use_oauth=False, allow_cache=True)`
     - New: `def __init__(self, client='WEB', use_oauth=False, allow_cache=True)`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

