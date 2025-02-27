# Hướng Dẫn Chạy Bot Trong Nền / Background Running Guide

## Tiếng Việt
### Phiên bản 1.2 - Chạy bot trong nền
Giờ đây bot đã có thể chạy trong nền mà không hiện cửa sổ console với phiên bản 1.2. [Tải tại đây](https://github.com/htch9999/discord-control-music-bot/releases/tag/v1.2)

### 1. Cài đặt
- Mở cửa sổ CMD (Command Prompt) và cài đặt PyInstaller bằng lệnh:
  ```sh
  pip install pyinstaller
  ```
- Lưu token của bạn vào file `token.json`.
- Chạy trực tiếp file `BACKGROUND.exe`. Bây giờ bot đã chạy trong nền, bạn có thể trải nghiệm.

### 2. Chỉnh sửa và tạo lại file chạy nền
- Nếu muốn chỉnh sửa bot, mở file `main.py` và thực hiện các thay đổi.
- Mở CMD (hoặc terminal), điều hướng đến thư mục chứa `main.py`:
  ```sh
  cd đường/dẫn/đến/thư_mục_của_bạn
  ```
- Sử dụng lệnh sau để tạo file chạy nền mới:
  ```sh
  python -m PyInstaller --noconsole --onefile main.py
  ```
- Sau khi hoàn thành, vào thư mục `dist`, lấy file `main.exe` và di chuyển nó vào thư mục chính của bot.
- Chạy `main.exe` để bot hoạt động trong nền.

Nếu có bất kỳ vấn đề hoặc thắc mắc gì, có thể liên hệ tôi để được trợ giúp:
- **Facebook**: [facebook.com/htch.9999](https://facebook.com/htch.9999)
- **Discord**: htch9999

---

## English
### Version 1.2 - Run bot in background
The bot can now run in the background without showing the console window in version 1.2. [Download here](https://github.com/htch9999/discord-control-music-bot/releases/tag/v1.2)

### 1. Installation
- Open CMD (Command Prompt) and install PyInstaller:
  ```sh
  pip install pyinstaller
  ```
- Save your token in the `token.json` file.
- Run `BACKGROUND.exe` directly. The bot will now run in the background.

### 2. Modify and rebuild the background executable
- If you want to modify the bot, edit the `main.py` file.
- Open CMD (or terminal), navigate to the folder containing `main.py`:
  ```sh
  cd path/to/your/folder
  ```
- Run the following command to create a new background executable:
  ```sh
  python -m PyInstaller --noconsole --onefile main.py
  ```
- Once completed, go to the `dist` folder, take the `main.exe` file, and move it to the main bot directory.
- Run `main.exe` to have the bot work in the background.

If you have any issues or questions, feel free to contact me for support:
- **Facebook**: [facebook.com/htch.9999](https://facebook.com/htch.9999)
- **Discord**: htch9999

Bot created by **htch9999**.

