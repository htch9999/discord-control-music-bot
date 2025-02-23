# discord-control-music-bot
Play music on your computer and control it with the discord bot!

Chương trình Python giúp mở nhạc trên máy tính, điều khiển qua bot discord, dành cho người lười chạy qua mở máy:))
Ý tưởng làm con bot này của mình xuất phát từ hồi xem được cái con bot tele mở nhạc của bác nào đó trong group. Vì mình thấy nó còn một số điểm khá là hạn chế, ví dụ như việc bot đó mở chrome hoặc brave lên để mở nhạc thì cũng khá bất tiện (theo một cách nào đó), và mình còn muốn mở nhạc khi mà thằng bạn đang mượn máy để chơi game :))

Các bước setup:
1. Cài đặt Python và module:
- tải xuống và cài đặt Python từ trang chủ chính thức (nên sử dụng phiên bản 3.11.9): https://www.python.org/downloads/
- Cài đặt các module cần thiết: discord.py, yt-dlp, asyncio và py-cord (pip install discord.py yt-dlp asyncio py-cord)
2. Cài đặt FFmpeg
- Tải FFmpeg từ trang chính thức: https://ffmpeg.org/download.html
- Giải nén và thêm thư mục bin vào biến môi trường PATH
3. Tải file của bot từ github của mình: https://github.com/htch9999/discord-control-music-bot
4. Tạo bot Discord
- Truy cập Discord Developer Portal: https://discord.com/developers/
- Nhấn New Application, đặt tên bot và nhấn Create.
- Chọn tab Bot -> nhấn Reset Token -> nhấn Yes, do it! để lấy token, sau đó lưu nó vào file token.json
- Tiếp tục kéo xuống mục Privileged Gateway Intents, bật Message Content Intent (trong tab bot đó)
- Trong tab Installation, ở phần Install Link, copy link ở đó và vào tab Oauth2 -> dán nó vào mục Redirects
- Vẫn trong tab Oauth2, ở phần URL Generator -> Chọn bot trong Scopes -> Trong Bot Permissions, chọn quyền: Read Messages History, Send Messages, Manager Messages
- Copy URL và dán vào trình duyệt để mời bot vào server.
5. Chạy bot:
- Mở file run.bat trong folder bot để mở cho nhanh, hoặc nếu muốn màu mè mất thời gian thì mọt người có thể vô cmd -> cd đến folder bot và chạy python main.py :))
- Đến một kênh bất kì trong server discord (nên tạo một kênh riêng) -> sử dụng lệnh !play <tên bài hát hoặc link>. Vì sau khi sử dụng lệnh này lần đầu thì bot sẽ lưu lại id tin nhắn chứa hàng chờ phát của bot và sẽ chỉnh sửa tin nhắn đó khi thêm hoặc xoá bài nhạc. Để có thể di chuyển tin nhắn đó sang kênh khác thì chỉ cần xoá tin nhắn cũ đó và sang kênh khác sử dụng lệnh !play.

------

CÁC LỆNH CỦA BOT
 !play {tên hoặc link} : phát nhạc (nếu có nhạc đang phát thì sẽ thêm vào hàng chờ), (có thể sử dụng tên video để tìm kiếm, link, link playlist youtube để thêm bài)
 !stop : dừng phát, xoá hàng chờ.
 !skip : bỏ qua bài đang phát và phát bài tiếp theo trong hàng chờ. 

-------

Đây là một dự án mình làm cho vui, mã nguồn mở nên các bác có thể tuỳ biến thoải mái. Có thể tích hợp thêm nircmd để điều chỉnh âm lượng bằng bot luôn nếu muốn:))
