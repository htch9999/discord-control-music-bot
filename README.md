# Discord Control Music Bot

---

## 🇬🇧 English

**Play and control music on your Windows PC via Discord!**  
Search, queue, skip, pause, adjust volume, and more—all from your Discord server.

### Features

- Play by name, link, or playlist (YouTube)
- Queue management: add, remove, skip, replay, clear
- Pause/Resume, Stop, Volume control
- Persistent queue/message, tray icon, background mode
- Active channel restriction, interactive Discord UI
- Auto message cleanup, multi-language

---

### 🚀 Installation

**Download:**  
- 👉 [Download the latest release (source code included)](https://github.com/htch9999/discord-control-music-bot/releases/latest)  

**Or build your own .exe:**  
- Install Python 3.11.9 and required modules:
  ```sh
  pip install discord.py yt-dlp py-cord pycaw pystray pillow psutil comtypes pyinstaller
  ```
- Build the bot into a single .exe (recommended for easy use & background mode):
  ```sh
  python -m PyInstaller --onefile --noconsole --icon=icon.png --add-data "icon.png;." main.py
  ```
- Use the generated `main.exe` file to run the bot (no console window, tray icon enabled).

**Or run with Python:**  
  ```sh
  python main.py
  ```

**Install FFmpeg:**  
- Download: https://ffmpeg.org/download.html  
- Extract and add the `bin` folder to your system `PATH`.

**Create Discord Bot & Token:**  
- Go to [Discord Developer Portal](https://discord.com/developers/)
- Create new application > Bot > Reset Token > Save token to `token.json`:
  ```json
  { "BOT_TOKEN": "YOUR_BOT_TOKEN_HERE" }
  ```
- Enable "Message Content Intent" in Bot settings.
- Use OAuth2 URL Generator to invite bot to your server with permissions:
  - Read Messages, Send Messages, Manage Messages

---

### 🕹️ Usage

1. In your chosen Discord channel, type:
   ```
   !activate
   ```
   *(This sets the current channel as the bot's active channel. All commands must be used here.)*
2. Now you can use all features and commands below!

**Basic Commands:**
- `!play <name/link>` – Play song or playlist (add to queue)
- `!p <name/link>` – Alias for `!play`
- `!skip` – Skip current song
- `!stop` – Stop and clear queue
- `!pause` – Pause/Resume
- `!h` – Show help

**Interactive Controls:**
- ➕: Add song
- ⏭️: Skip
- 🛑: Stop
- ⏯️: Pause/Resume
- 🔁: Replay current song
- 🔉 / 🔊: Volume down/up
- 🗑️: Remove song from queue

---

### 💾 Persistence & Tray Icon

- The bot saves the queue and message state to disk. If you close the bot (via tray icon or exit), it will restore the queue/message on next start.
- Tray icon (bottom right of Windows): right-click to save & exit, or exit immediately.

---

### 🛠️ Advanced

- **Background/Tray Mode**: Bot runs in background, no console window.
- **Auto-cleanup**: Bot deletes command messages and invalid messages for a clean channel.

---

### ❓ FAQ

- **Q: Does the bot play music in Discord voice channels?**  
  **A:** No, it plays music on your PC and lets you control it via Discord.
- **Q: Can I use Spotify/SoundCloud?**  
  **A:** Only YouTube (video, playlist, search) is supported.
- **Q: How to move the queue message to another channel?**  
  **A:** Delete the old message, use `!activate` in the new channel.

---

### 🧑‍💻 Credits & Support

Bot created by **htch9999**. If there is any problem, please contact us via:
- **Facebook**: https://www.facebook.com/htch.9999/
- **Discord**: htch9999

**Support me:**  
- [Buy Me a Coffee](https://buymeacoffee.com/htch9999)  
- [MoMo Donation](https://me.momo.vn/htch9999)

---

### 📝 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🇻🇳 Tiếng Việt

**Phát và điều khiển nhạc trên máy tính Windows qua Discord!**  
Tìm kiếm, thêm hàng chờ, bỏ qua, tạm dừng, chỉnh âm lượng... tất cả từ Discord.

### Tính năng

- Phát nhạc theo tên, link, playlist (YouTube)
- Quản lý hàng chờ: thêm, xoá, bỏ qua, phát lại, xoá hàng chờ
- Tạm dừng/tiếp tục, dừng, chỉnh âm lượng
- Lưu trạng thái, chạy nền với icon khay hệ thống
- Chỉ hoạt động ở kênh mặc định, giao diện nút trực quan
- Tự động xoá tin nhắn, đa ngôn ngữ

---

### 🚀 Hướng dẫn cài đặt

**Tải về:**  
- 👉 [Tải bản phát hành mới nhất (đã có kèm cả mã nguồn)](https://github.com/htch9999/discord-control-music-bot/releases/latest)  

**Hoặc tự build file .exe:**  
- Cài Python 3.11.9 và các thư viện:
  ```sh
  pip install discord.py yt-dlp py-cord pycaw pystray pillow psutil comtypes pyinstaller
  ```
- Build bot thành file .exe (khuyên dùng để chạy nền, không hiện cửa sổ):
  ```sh
  python -m PyInstaller --onefile --noconsole --icon=icon.png --add-data "icon.png;." main.py
  ```
- Sử dụng file `main.exe` để chạy bot (không hiện console, có icon khay hệ thống).

**Hoặc chạy trực tiếp bằng Python:**  
  ```sh
  python main.py
  ```

**Cài FFmpeg:**  
- Tải tại: https://ffmpeg.org/download.html  
- Giải nén và thêm thư mục `bin` vào biến môi trường `PATH`.

**Tạo bot Discord & Token:**  
- Vào [Discord Developer Portal](https://discord.com/developers/)
- Tạo ứng dụng mới > Bot > Reset Token > Lưu vào `token.json`:
  ```json
  { "BOT_TOKEN": "YOUR_BOT_TOKEN_HERE" }
  ```
- Bật "Message Content Intent" trong cài đặt Bot.
- Dùng OAuth2 URL Generator để mời bot vào server với quyền:
  - Read Messages, Send Messages, Manage Messages

---

### 🕹️ Hướng dẫn sử dụng

1. Vào kênh Discord bạn muốn, gõ:
   ```
   !activate
   ```
   *(Đặt kênh hiện tại làm kênh mặc định. Mọi lệnh phải dùng tại đây.)*
2. Bây giờ bạn có thể sử dụng tất cả các tính năng và lệnh bên dưới!

**Lệnh cơ bản:**
- `!play <tên hoặc link>` – Phát nhạc/playlist (thêm vào hàng chờ)
- `!p <tên hoặc link>` – Alias cho `!play`
- `!skip` – Bỏ qua bài hiện tại
- `!stop` – Dừng và xoá hàng chờ
- `!pause` – Tạm dừng/tiếp tục
- `!h` – Hướng dẫn

**Điều khiển bằng nút:**
- ➕: Thêm bài hát
- ⏭️: Bỏ qua
- 🛑: Dừng
- ⏯️: Tạm dừng/tiếp tục
- 🔁: Phát lại bài hiện tại
- 🔉 / 🔊: Giảm/Tăng âm lượng
- 🗑️: Xoá bài khỏi hàng chờ

---

### 💾 Lưu trạng thái & chạy nền

- Bot sẽ tự động lưu hàng chờ và trạng thái tin nhắn. Khi tắt bot (qua icon khay hệ thống hoặc thoát), hàng chờ sẽ được khôi phục khi mở lại.
- Icon khay hệ thống (góc phải dưới Windows): click chuột phải để lưu & thoát, hoặc thoát ngay.

---

### 🛠️ Nâng cao

- **Chạy nền/Tray Mode**: Bot chạy nền, không hiện cửa sổ.
- **Tự động dọn dẹp**: Bot tự xoá lệnh và tin nhắn không hợp lệ để kênh sạch sẽ.

---

### ❓ Câu hỏi thường gặp

- **Bot có phát nhạc trong voice channel không?**  
  Không, bot phát nhạc trên máy tính của bạn và điều khiển qua Discord.
- **Có hỗ trợ Spotify/SoundCloud không?**  
  Chỉ hỗ trợ YouTube (video, playlist, tìm kiếm).
- **Muốn chuyển tin nhắn hàng chờ sang kênh khác?**  
  Xoá tin nhắn cũ, dùng `!activate` ở kênh mới.

---

### 🧑‍💻 Liên hệ & Ủng hộ

Bot tạo bởi **htch9999**. Nếu có bất kì vấn đề gì, có thể liên hệ qua:
- **Facebook**: https://www.facebook.com/htch.9999/
- **Discord**: htch9999

**Ủng hộ mình:**  
- [Buy Me a Coffee](https://buymeacoffee.com/htch9999)  
- [MoMo Donation](https://me.momo.vn/htch9999)

---

### 📝 License

MIT License. Xem [LICENSE](LICENSE) để biết chi tiết.

---

Enjoy your music! / Chúc bạn nghe nhạc vui vẻ!
