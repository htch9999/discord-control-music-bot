# Discord Control Music Bot

---

<div style="display: flex; gap: 2em;">
  <div style="flex: 1;">
    <h2>🇬🇧 English</h2>
    <b>Play and control music on your Windows PC via Discord!</b><br>
    Search, queue, skip, pause, adjust volume, and more—all from your Discord server.<br>
    <ul>
      <li>Play by name, link, or playlist (YouTube)</li>
      <li>Queue management: add, remove, skip, replay, clear</li>
      <li>Pause/Resume, Stop, Volume control</li>
      <li>Persistent queue/message, tray icon, background mode</li>
      <li>Active channel restriction, interactive Discord UI</li>
      <li>Auto message cleanup, multi-language</li>
    </ul>
  </div>
  <div style="flex: 1;">
    <h2>🇻🇳 Tiếng Việt</h2>
    <b>Phát và điều khiển nhạc trên máy tính Windows qua Discord!</b><br>
    Tìm kiếm, thêm hàng chờ, bỏ qua, tạm dừng, chỉnh âm lượng... tất cả từ Discord.<br>
    <ul>
      <li>Phát nhạc theo tên, link, playlist (YouTube)</li>
      <li>Quản lý hàng chờ: thêm, xoá, bỏ qua, phát lại, xoá hàng chờ</li>
      <li>Tạm dừng/tiếp tục, dừng, chỉnh âm lượng</li>
      <li>Lưu trạng thái, chạy nền với icon khay hệ thống</li>
      <li>Chỉ hoạt động ở kênh mặc định, giao diện nút trực quan</li>
      <li>Tự động xoá tin nhắn, đa ngôn ngữ</li>
    </ul>
  </div>
</div>

---

## 🚀 Installation / Cài đặt

**Download:**  
- 👉 [Download the latest release (.zip or .exe)](https://github.com/htch9999/discord-control-music-bot/releases/latest)  
  *(Always use the latest release instead of cloning the repo!)*

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

**Hoặc chạy trực tiếp bằng Python:**  
- Tải Python 3.11.9 và các thư viện như trên.
- Chạy:
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

## 🕹️ Usage / Sử dụng

<div style="display: flex; gap: 2em;">
  <div style="flex: 1;">
    <h3>🇬🇧 English</h3>
    <ol>
      <li>In your chosen Discord channel, type:<br>
        <code>!activate</code><br>
        <i>(This sets the current channel as the bot's active channel. All commands must be used here.)</i>
      </li>
      <li>Now you can use all features and commands below!</li>
    </ol>
    <b>Basic Commands:</b>
    <ul>
      <li><code>!play &lt;name/link&gt;</code> – Play song or playlist (add to queue)</li>
      <li><code>!p &lt;name/link&gt;</code> – Alias for <code>!play</code></li>
      <li><code>!skip</code> – Skip current song</li>
      <li><code>!stop</code> – Stop and clear queue</li>
      <li><code>!pause</code> – Pause/Resume</li>
      <li><code>!h</code> – Show help</li>
    </ul>
    <b>Interactive Controls:</b>
    <ul>
      <li>➕: Add song</li>
      <li>⏭️: Skip</li>
      <li>🛑: Stop</li>
      <li>⏯️: Pause/Resume</li>
      <li>🔁: Replay current song</li>
      <li>🔉 / 🔊: Volume down/up</li>
      <li>🗑️: Remove song from queue</li>
    </ul>
  </div>
  <div style="flex: 1;">
    <h3>🇻🇳 Tiếng Việt</h3>
    <ol>
      <li>Vào kênh Discord bạn muốn, gõ:<br>
        <code>!activate</code><br>
        <i>(Đặt kênh hiện tại làm kênh mặc định. Mọi lệnh phải dùng tại đây.)</i>
      </li>
      <li>Bây giờ bạn có thể sử dụng tất cả các tính năng và lệnh bên dưới!</li>
    </ol>
    <b>Lệnh cơ bản:</b>
    <ul>
      <li><code>!play &lt;tên hoặc link&gt;</code> – Phát nhạc/playlist (thêm vào hàng chờ)</li>
      <li><code>!p &lt;tên hoặc link&gt;</code> – Alias cho <code>!play</code></li>
      <li><code>!skip</code> – Bỏ qua bài hiện tại</li>
      <li><code>!stop</code> – Dừng và xoá hàng chờ</li>
      <li><code>!pause</code> – Tạm dừng/tiếp tục</li>
      <li><code>!h</code> – Hướng dẫn</li>
    </ul>
    <b>Điều khiển bằng nút:</b>
    <ul>
      <li>➕: Thêm bài hát</li>
      <li>⏭️: Bỏ qua</li>
      <li>🛑: Dừng</li>
      <li>⏯️: Tạm dừng/tiếp tục</li>
      <li>🔁: Phát lại bài hiện tại</li>
      <li>🔉 / 🔊: Giảm/Tăng âm lượng</li>
      <li>🗑️: Xoá bài khỏi hàng chờ</li>
    </ul>
  </div>
</div>

---

## 💾 Persistence & Tray Icon / Lưu trạng thái & chạy nền

- The bot saves the queue and message state to disk. If you close the bot (via tray icon or exit), it will restore the queue/message on next start.
- Tray icon (bottom right of Windows): right-click to save & exit, or exit immediately.

---

## 🛠️ Advanced / Nâng cao

- **Background/Tray Mode**: Bot runs in background, no console window.
- **Auto-cleanup**: Bot deletes command messages and invalid messages for a clean channel.
- **Multi-server support**: Each server can have its own queue/message.

---

## ❓ FAQ

- **Q: Does the bot play music in Discord voice channels?**
  - **A:** No, it plays music on your PC and lets you control it via Discord.
- **Q: Can I use Spotify/SoundCloud?**
  - **A:** Only YouTube (video, playlist, search) is supported.
- **Q: How to move the queue message to another channel?**
  - **A:** Delete the old message, use `!activated` in the new channel.

---

## 🧑‍💻 Credits & Support / Liên hệ & Ủng hộ

Bot created by **htch9999**  
- **Facebook**: https://www.facebook.com/htch.9999/
- **Discord**: htch9999

**Support me / Ủng hộ mình:**  
- [Buy Me a Coffee](https://buymeacoffee.com/htch9999)  
- [MoMo Donation](https://me.momo.vn/htch9999)

---

## 📝 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🇻🇳 Tiếng Việt

### Mục đích

Bot giúp bạn phát nhạc trên máy tính Windows và điều khiển từ xa qua Discord. Lý tưởng cho phòng làm việc, phòng net, hoặc ai lười đứng dậy chuyển bài nhạc!

### Tính năng nổi bật

- Tìm kiếm, phát nhạc, playlist YouTube
- Quản lý hàng chờ, bỏ qua, tạm dừng, phát lại, xoá bài
- Điều chỉnh âm lượng hệ thống
- Lưu trạng thái hàng chờ, tự động khôi phục khi khởi động lại
- Chạy nền với icon ở khay hệ thống
- Chỉ hoạt động ở kênh mặc định nếu muốn
- Giao diện nút bấm trực quan trên Discord

### Hướng dẫn cài đặt

1. Cài Python 3.11.9 và các thư viện cần thiết:
   ```sh
   pip install discord.py yt-dlp py-cord pycaw pystray pillow psutil comtypes
   ```
2. Cài FFmpeg, thêm vào PATH.
3. Tạo bot Discord, lấy token, lưu vào `token.json`.
4. Chạy bot bằng `python main.py`.

### Lệnh sử dụng

- `!play <tên hoặc link>`: Phát nhạc/playlist
- `!p <tên hoặc link>`: Alias cho play
- `!skip`: Bỏ qua bài hiện tại
- `!stop`: Dừng và xoá hàng chờ
- `!pause`: Tạm dừng/tiếp tục
- `!activate`: Đặt kênh mặc định
- `!h`: Hướng dẫn

### Hỗ trợ

- Facebook: https://www.facebook.com/htch.9999/
- Discord: htch9999

Ủng hộ mình tại:
- [Momo](https://me.momo.vn/htch9999)
- [Buy me a coffee](https://buymeacoffee.com/htch9999)

---

Enjoy your music! / Chúc bạn nghe nhạc vui vẻ!
