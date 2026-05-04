⚠️ Archived – Learning/Experimental Project

Built during an earlier exploration phase.
Left as-is for reference; not actively maintained.
May not work with newer Telegram Bot API changes or modern environments without modifications.

# M3U8 Telegram Downloader Bot

A simple Telegram bot (Python) that downloads and processes `.m3u8` video streams (VOD/live) and sends the final video back to the user.

---

## Features

- Accepts m3u8 URLs via Telegram
- Supports VOD downloads
- Supports live stream recording (basic)
- Queue-based request handling
- Automatic video concatenation and sending

---

## Setup

### 1. Install dependencies

```bash
pip3 install -r requirements.txt
````

---

### 2. Configure bot

Edit the following files:

#### `session.py`

Set your Telegram user ID:

```python
adminId = "YOUR_TELEGRAM_USER_ID"
```

#### `utils/bot_config.py`

Set your bot token:

```python
teletoken = "YOUR_BOT_TOKEN"
```

You can get a bot token from: @BotFather on Telegram

---

## Run the bot

```bash
python3 tele_bot.py
```

---

## Usage

Once running, open Telegram and chat with your bot:

* Send a valid `.m3u8` URL
* Bot will queue and process it
* Downloaded video will be sent back automatically

### Commands

* `/start` → Start interaction
* `/clear` → Cancel current request
* `/queue` → Check queue position
* `/log` → (admin only) view logs
