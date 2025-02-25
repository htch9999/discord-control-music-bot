# discord-control-music-bot

## English
Play music on your computer and control it with a Discord bot!

This Python program allows you to play music on your computer and control it via a Discord bot, perfect for those who don't want to keep running back to their computer just to change the song!

### Setup Instructions:
1. Install Python and required modules:
   - Download and install Python from the official website (recommended version: 3.11.9): https://www.python.org/downloads/
   - Install required modules: discord.py, yt-dlp, asyncio, and py-cord
     ```sh
     pip install discord.py yt-dlp asyncio py-cord
     ```
2. Install FFmpeg:
   - Download FFmpeg from the official website: https://ffmpeg.org/download.html
   - Extract and add the `bin` folder to the system PATH variable
3. Download the bot files from my GitHub repository an unzip it: https://github.com/htch9999/discord-control-music-bot
4. Create a Discord bot:
   - Go to the Discord Developer Portal: https://discord.com/developers/
   - Click "New Application," name your bot, and click "Create."
   - In the "Bot" tab, click "Reset Token," confirm, and save the token in `token.json`
   - Scroll down to "Privileged Gateway Intents" and enable "Message Content Intent"
   - In the "Installation" tab, copy the link from "Install Link" and paste it into the "Redirects" section of the "OAuth2" tab
   - In "OAuth2" -> "URL Generator":
     - Select "bot" under "Scopes"
     - Under "Bot Permissions," select:
       - Read Messages History
       - Send Messages
       - Manage Messages
     - Copy the generated URL, paste it into your browser, and invite the bot to your server.
5. Running the bot:
   - Open `run.bat` in the bot folder for quick startup, or manually run:
     ```sh
     cd /path-to-bot
     python main.py
     ```
   - In any Discord channel (preferably a dedicated one), use `!play <song name or link>`. The bot will store the message ID containing the queue and update it accordingly. If you want to move the message to another channel, delete the old message and use `!play` in the new channel.

### Bot Commands:
- `!play {name or link}` - Play music (adds to the queue if music is already playing). Supports video search, direct links, and YouTube playlists.
- `!stop` - Stop playback and clear the queue.
- `!skip` - Skip the current song and play the next one in the queue.

Bot created by **htch9999**. For any questions or contributions, contact me:
- **Facebook**: https://www.facebook.com/htch.9999/
- **Discord**: htch9999

---

## Tiếng Việt
Chơi nhạc trên máy tính và điều khiển bằng bot Discord!

Chương trình Python giúp mở nhạc trên máy tính và điều khiển qua bot Discord, lý tưởng cho những ai lười và không muốn phải chạy qua lại để chuyển bài nhạc :))

### Hướng dẫn cài đặt:
1. Cài đặt Python và các module cần thiết:
   - Tải và cài đặt Python từ trang chủ: https://www.python.org/downloads/ (phiên bản khuyên dùng: 3.11.9)
   - Cài đặt các module: discord.py, yt-dlp, asyncio, py-cord
     ```sh
     pip install discord.py yt-dlp asyncio py-cord
     ```
2. Cài đặt FFmpeg:
   - Tải FFmpeg từ trang chính thức: https://ffmpeg.org/download.html
   - Giải nén và thêm thư mục `bin` vào biến môi trường PATH
3. Tải file bot từ GitHub và giải nén: https://github.com/htch9999/discord-control-music-bot
4. Tạo bot Discord:
   - Truy cập Discord Developer Portal: https://discord.com/developers/
   - Nhấn "New Application," đặt tên bot và nhấn "Create."
   - Trong tab "Bot," nhấn "Reset Token," xác nhận, và lưu token vào `token.json`
   - Kéo xuống mục "Privileged Gateway Intents" và bật "Message Content Intent"
   - Trong tab "Installation," copy link từ "Install Link" và dán vào mục "Redirects" trong tab "OAuth2"
   - Trong "OAuth2" -> "URL Generator":
     - Chọn "bot" trong "Scopes"
     - Trong "Bot Permissions," chọn:
       - Read Messages History
       - Send Messages
       - Manage Messages
     - Copy URL, dán vào trình duyệt để mời bot vào server.
5. Chạy bot:
   - Mở `run.bat` trong folder bot hoặc chạy thủ công nếu bạn thích màu mè mất thời gian:)
     ```sh
     cd /duong-dan-toi-bot
     python main.py
     ```
   - Vào một kênh Discord (nên tạo kênh riêng), dùng `!play <tên bài hát hoặc link>`

### Lệnh Bot:
- `!play {tên hoặc link}` - Phát nhạc, hỗ trợ tìm kiếm, link, playlist youtube.
- `!stop` - Dừng nhạc và xoá hàng chờ.
- `!skip` - Bỏ qua bài hát hiện tại.

Bot tạo bởi **htch9999**. Liên hệ:
- **Facebook**: https://www.facebook.com/htch.9999/
- **Discord**: htch9999

