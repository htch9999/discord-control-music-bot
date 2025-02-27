# Hướng Dẫn Chạy Bot Trong Nền (BACKGROUND RUNNING)

## Giới Thiệu
Từ phiên bản **1.2**, bot đã hỗ trợ chạy trong nền mà không hiển thị cửa sổ console.

🔗 **Tải phiên bản 1.2 tại đây:** [link tải](https://github.com/htch9999/discord-control-music-bot/releases/tag/v1.2)

---

## Cách 1: Chạy Bot Trực Tiếp
1. Lưu token của bạn vào file `token.json`.
2. Chạy file `BACKGROUND.exe`.
3. Bây giờ bot đã chạy trong nền, bạn có thể trải nghiệm.

---

## Cách 2: Tuỳ Chỉnh Và Chạy Bot Trong Nền
Nếu bạn muốn chỉnh sửa code bot trước khi chạy, hãy làm theo các bước sau:

1. Chỉnh sửa file `main.py` theo ý muốn.
2. Mở **Command Prompt (cmd) hoặc Terminal**.
3. Điều hướng đến thư mục chứa file `main.py` bằng lệnh:
   ```sh
   cd đường-dẫn-đến-thư-mục-bot
   ```
4. Chạy lệnh sau để tạo tệp chạy dưới nền:
   ```sh
   python -m PyInstaller --noconsole --onefile .\main.py
   ```
5. Sau khi hoàn tất, truy cập thư mục `dist/main.exe`, di chuyển nó vào thư mục chính của bot.
6. Chạy `main.exe`, bot sẽ chạy dưới nền.

---

## Hỗ Trợ
Nếu bạn gặp bất kỳ vấn đề hoặc thắc mắc nào, hãy liên hệ tôi để được trợ giúp:
- **Facebook:** [facebook.com/htch.9999](https://facebook.com/htch.9999)
- **Discord:** `htch9999`

Bot được tạo bởi **htch9999**.

---

# BACKGROUND RUNNING GUIDE

## Introduction
Starting from **version 1.2**, the bot now supports running in the background without showing the console window.

🔗 **Download version 1.2 here:** [download link](https://github.com/htch9999/discord-control-music-bot/releases/tag/v1.2)

---

## Method 1: Run the Bot Directly
1. Save your token in `token.json`.
2. Run `BACKGROUND.exe`.
3. The bot is now running in the background, enjoy!

---

## Method 2: Customize and Run the Bot in the Background
If you want to modify the bot before running, follow these steps:

1. Edit the `main.py` file as needed.
2. Open **Command Prompt (cmd) or Terminal**.
3. Navigate to the bot folder using:
   ```sh
   cd path-to-bot-folder
   ```
4. Run the following command to create a background executable:
   ```sh
   python -m PyInstaller --noconsole --onefile .\main.py
   ```
5. Once completed, go to `dist/main.exe`, move it to the main bot folder.
6. Run `main.exe`, and the bot will run in the background.

---

## Support
If you encounter any issues or have questions, feel free to contact me for assistance:
- **Facebook:** [facebook.com/htch.9999](https://facebook.com/htch.9999)
- **Discord:** `htch9999`

Bot created by **htch9999**.

