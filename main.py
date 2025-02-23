import discord
from discord.ext import commands
from discord.ui import Button, View
import subprocess
import threading
import yt_dlp
import asyncio
import datetime
import json
import os
import time
# Đọc token từ file config.json
with open("token.json", "r") as config_file:
    config = json.load(config_file)

bot_token = config["BOT_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

queue = []  # Danh sách hàng chờ
is_playing = False  # Trạng thái đang phát nhạc
current_song = None  # Bài nhạc đang phát
queue_message = None  # Tin nhắn embed hiển thị hàng chờ

# Đường dẫn file lưu ID tin nhắn
QUEUE_MESSAGE_FILE = "queue_message.json"

def save_queue_message_id(message_id):
    """Lưu ID tin nhắn vào file JSON"""
    data = {"queue_message_id": message_id}
    with open(QUEUE_MESSAGE_FILE, "w") as file:
        json.dump(data, file)

def load_queue_message_id():
    """Đọc ID tin nhắn từ file JSON"""
    if os.path.exists(QUEUE_MESSAGE_FILE):
        with open(QUEUE_MESSAGE_FILE, "r") as file:
            data = json.load(file)
            return data.get("queue_message_id")
    return None

def get_playlist_videos(playlist_url):
    """
    Lấy danh sách video từ một playlist YouTube.
    """
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=False)
        if "entries" in playlist_info:
            return [
                {"title": video["title"], "url": video["url"]}
                for video in playlist_info["entries"]
            ]
    return []


def get_video_info(url):
    """
    Lấy thông tin video bằng yt-dlp.
    """
    ydl_opts = {"quiet": True, "format": "bestaudio"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title", "Unknown Title"),
            "duration": info.get("duration", 0)
        }

def run_command_with_progress(url):
    """
    Chạy lệnh yt-dlp và ffplay để phát nhạc.
    """
    try:
        yt_dlp_cmd = [
            "yt-dlp", "-f", "bestaudio", "--extract-audio", "--audio-quality", "0",
            "--quiet", "--no-warnings", "--output", "-",
            url
        ]
        ffplay_cmd = [
            "ffplay", "-i", "pipe:0", "-nodisp", "-autoexit", "-loglevel", "error"
        ]

        # Chạy yt-dlp và ffplay
        yt_dlp_proc = subprocess.Popen(yt_dlp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ffplay_proc = subprocess.Popen(ffplay_cmd, stdin=yt_dlp_proc.stdout)

        # Đợi quá trình ffplay hoàn thành
        ffplay_proc.wait()

        # Đóng yt-dlp
        yt_dlp_proc.terminate()

    except Exception as e:
        print(f"Lỗi khi phát nhạc: {e}")


async def play_next(ctx):
    """
    Phát bài tiếp theo trong hàng chờ.
    """
    global is_playing, queue, current_song, queue_message

    if not queue:
        is_playing = False
        current_song = None
        await update_queue_message(ctx)
        return

    current_song = queue[0]  # Lấy bài đầu tiên trong hàng chờ
    await update_queue_message(ctx)

    is_playing = True
    url = current_song["url"]

    # Lấy thông tin video
    video_info = get_video_info(url)
    title = video_info["title"]
    duration_seconds = video_info["duration"]
    duration_formatted = str(datetime.timedelta(seconds=duration_seconds))

    print(f"\n\n--------------------------------------------------------------------------")

    print(f"\n🎵 Đang phát: {title}")
    print(f"🕒 Tổng thời lượng: {duration_formatted}")

    def play_song():
        """
        Chạy yt-dlp và ffplay để phát nhạc.
        """
        yt_dlp_cmd = [
            "yt-dlp", "-f", "bestaudio", "--extract-audio", "--audio-quality", "0",
            "--quiet", "--no-warnings", "--output", "-",
            url
        ]
        ffplay_cmd = [
            "ffplay", "-i", "pipe:0", "-nodisp", "-autoexit", "-loglevel", "error"
        ]

        yt_dlp_proc = subprocess.Popen(yt_dlp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ffplay_proc = subprocess.Popen(ffplay_cmd, stdin=yt_dlp_proc.stdout)

        yt_dlp_proc.stdout.close()  # Đóng output yt-dlp để tránh rò rỉ bộ nhớ

        # Bước 1: Hiển thị trạng thái chờ
        time.sleep(3)  # Đứng yên 3 giây

        # Bước 2: Cập nhật thời gian thực
        start_time = time.perf_counter()
        track_progress(start_time, duration_seconds)

        ffplay_proc.wait()  # Đợi ffplay kết thúc

        asyncio.run_coroutine_threadsafe(finish_song(ctx), bot.loop)

    def track_progress(start_time, duration):
        """
        Cập nhật thời gian phát trong console (chạy đồng thời với ffplay).
        """
        while is_playing:
            elapsed_time = int(time.perf_counter() - start_time)

            if elapsed_time >= duration:
                break

            time.sleep(1)  # Cập nhật mỗi giây

    # Chạy song song phát nhạc và cập nhật thời gian
    threading.Thread(target=play_song, daemon=True).start()



async def finish_song(ctx):
    """
    Kết thúc bài nhạc hiện tại và chuyển bài tiếp theo.
    """
    global is_playing, queue, current_song
    queue.pop(0)  # Xóa bài hiện tại khỏi hàng chờ
    current_song = None
    is_playing = False
    await play_next(ctx)

class QueueControlView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    @discord.ui.button(label="🛑", style=discord.ButtonStyle.secondary)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global is_playing, queue, current_song

        await interaction.response.defer()

        is_playing = False
        queue.clear()
        current_song = None

        subprocess.run(["taskkill", "/IM", "ffplay.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        queue_message_id = load_queue_message_id()
        if queue_message_id:
            try:
                queue_message = await self.ctx.channel.fetch_message(queue_message_id)
                embed = discord.Embed(title="🎵 Hàng chờ phát nhạc", color=discord.Color.blurple())
                embed.description = "Hàng chờ trống."
                await queue_message.edit(embed=embed, view=self)
            except discord.NotFound:
                pass

    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.secondary)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global is_playing, queue, current_song

        await interaction.response.defer()  # Tránh lỗi interaction timeout

        if is_playing and queue:
            subprocess.run(["taskkill", "/IM", "ffplay.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if len(queue) > 1:  # Còn bài tiếp theo
                queue.pop(0)  # Xóa bài hiện tại khỏi hàng chờ
                current_song = queue[0]  # Chuyển sang bài tiếp theo
                await play_next(self.ctx)  # Phát tiếp
            else:
                current_song = None
                is_playing = False  # Không còn gì để phát
                await update_queue_message(self.ctx)  # Cập nhật hàng chờ trống
        else:
            await interaction.followup.send("🎵 Không có bài hát nào đang phát để bỏ qua.", ephemeral=True)

async def update_queue_message(ctx):
    global queue_message_id, queue, current_song

    queue_message_id = load_queue_message_id()

    queue_message = None
    if queue_message_id:
        try:
            queue_message = await ctx.fetch_message(queue_message_id)
        except discord.NotFound:
            queue_message = None

    if not queue_message:
        embed = discord.Embed(title="🎵 Hàng chờ phát nhạc", color=discord.Color.blurple())
        embed.description = "Hàng chờ trống." if not queue else f"**Đang phát: {queue[0]['title']}**\n\n"
        next_songs = queue[1:11]
        if next_songs:
            embed.description += "**Tiếp theo:**\n" + "\n".join([f"  **#{i + 1}:** {song['title']}" for i, song in enumerate(next_songs)])

        if queue:
            embed.set_footer(text=f"📊 Tổng số bài trong hàng chờ: {len(queue)}")

        queue_message = await ctx.send(embed=embed, view=QueueControlView(ctx))
        queue_message_id = queue_message.id
        save_queue_message_id(queue_message_id)

    embed = discord.Embed(title="🎵 Hàng chờ phát nhạc", color=discord.Color.blurple())

    if not queue:
        embed.description = "Hàng chờ trống."
    else:
        embed.description = f"**Đang phát: {queue[0]['title']}**\n\n"
        next_songs = queue[1:11]
        if next_songs:
            embed.description += "**Tiếp theo:**\n" + "\n".join([f"  **#{i + 1}:** {song['title']}" for i, song in enumerate(next_songs)])

        embed.set_footer(text=f"📊 Tổng số bài trong hàng chờ: {len(queue)}")

    await queue_message.edit(embed=embed, view=QueueControlView(ctx))

@bot.event
async def on_ready():
    print(f"Bot đã sẵn sàng! Đăng nhập với tên: {bot.user}")

import asyncio
import datetime
import discord
import yt_dlp
from discord.ext import commands

@bot.command(name="play")
async def play(ctx, *, query: str):
    """
    Nhận lệnh từ Discord, tìm video hoặc phát nhạc qua URL.
    Hỗ trợ cả tìm kiếm, link video và link playlist.
    """
    global queue, is_playing
    request_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    await ctx.message.delete()
    is_url = query.startswith("http://") or query.startswith("https://")

    # Xử lý URL playlist
    if is_url and "playlist" in query:
        embed_loading = discord.Embed(
            title="📜 Đang xử lý playlist...",
            description="Vui lòng chờ trong giây lát...",
            color=discord.Color.orange()
        )
        loading_msg = await ctx.send(embed=embed_loading)

        try:
            playlist_videos = await asyncio.to_thread(get_playlist_videos, query)
        except Exception as e:
            playlist_videos = None
            print(f"Lỗi lấy playlist: {e}")

        if not playlist_videos:
            embed_error = discord.Embed(
                title="❌ Lỗi!",
                description="Không thể lấy danh sách video từ playlist này.",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed_error)
            await asyncio.sleep(5)
            await loading_msg.delete()
            return

        queue.extend(playlist_videos)  # Thêm toàn bộ playlist vào hàng chờ
        await update_queue_message(ctx)

        embed_success = discord.Embed(
            title="✅ Playlist đã được thêm vào hàng chờ!",
            description=f"**{len(playlist_videos)} bài hát đã được thêm**",
            color=discord.Color.green()
        )
        await loading_msg.edit(embed=embed_success)
        await asyncio.sleep(5)
        await loading_msg.delete()
        return  # Kết thúc tại đây để không làm ảnh hưởng đến cách xử lý khác

    # Nếu không phải playlist, tiếp tục xử lý tìm kiếm/video đơn lẻ
    search_message = None
    if not is_url:
        embed_search = discord.Embed(
            title="🎵 Đang tìm kiếm...",
            description=f"**{query}**",
            color=discord.Color.blue()
        )
        embed_search.set_footer(text=f"Yêu cầu bởi: {ctx.author} | Thời gian: {request_time}")
        search_message = await ctx.send(embed=embed_search)

    if is_url:
        url = query
        video_info = get_video_info(url)
    else:
        # Tìm kiếm trên YouTube với timeout
        def search_youtube(q):
            try:
                with yt_dlp.YoutubeDL({"quiet": True, "noplaylist": True, "timeout": 5}) as ydl:
                    result = ydl.extract_info(f"ytsearch:{q}", download=False)
                    return result['entries'][0] if 'entries' in result else None
            except Exception as e:
                print(f"Lỗi tìm kiếm YouTube: {e}")
                return None

        video = await asyncio.to_thread(search_youtube, query)
        if not video:
            embed_error = discord.Embed(
                title="❌ Lỗi!",
                description=f"Không tìm thấy video nào khớp với từ khóa: **{query}**.",
                color=discord.Color.red()
            )
            embed_error.set_footer(text=f"Yêu cầu bởi: {ctx.author} | Thời gian: {request_time}")
            if search_message:
                await search_message.edit(embed=embed_error)
                await asyncio.sleep(5)
                await search_message.delete()
            else:
                await ctx.send(embed=embed_error)
            return

        url = video['webpage_url']
        video_info = {
            "title": video['title'],
            "duration": video['duration'],
        }

    queue.append({"title": video_info["title"], "url": url})
    await update_queue_message(ctx)

    # Nếu bot tìm kiếm bằng tên, cập nhật tin nhắn thay vì xóa ngay
    if search_message:
        embed_found = discord.Embed(
            title="✅ Đã tìm thấy!",
            description=f"**{video_info['title']}**",
            color=discord.Color.green()
        )
        embed_found.set_footer(text=f"Yêu cầu bởi: {ctx.author} | Thời gian: {request_time}")
        await search_message.edit(embed=embed_found)
        await asyncio.sleep(5)
        await search_message.delete()

    # Nếu bot chưa phát nhạc, bắt đầu ngay
    if not is_playing:
        await play_next(ctx)


@bot.command(name="skip")
async def skip(ctx):
    """
    Bỏ qua bài hát hiện tại và phát bài tiếp theo trong hàng chờ.
    """
    global is_playing, queue
    await ctx.message.delete()  # Xóa tin nhắn yêu cầu của người dùng

    if is_playing:
        is_playing = False
        subprocess.run(["taskkill", "/IM", "ffplay.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # Dừng ffplay
        await finish_song(ctx)  # Kết thúc bài hát hiện tại và chuyển bài tiếp theo
        skip_message = await ctx.send("⏭️ Đã bỏ qua bài hát và chuyển sang bài tiếp theo.")
    else:
        skip_message = await ctx.send("🎵 Không có bài hát nào đang phát để bỏ qua.")

    await asyncio.sleep(5)
    await skip_message.delete()  # Xóa tin nhắn của bot sau 5 giây

@bot.command(name="stop")
async def stop(ctx):
    """
    Dừng phát nhạc.
    """
    global is_playing, queue, current_song
    is_playing = False
    queue.clear()
    current_song = None

    # Gửi lệnh dừng tới ffplay
    subprocess.run(["taskkill", "/IM", "ffplay.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Xoá tin nhắn yêu cầu của người dùng
    await ctx.message.delete()

    # Lấy ID tin nhắn từ file và cập nhật
    queue_message_id = load_queue_message_id()
    if queue_message_id:
        try:
            queue_message = await ctx.channel.fetch_message(queue_message_id)
            embed = discord.Embed(title="🎵 Hàng chờ phát nhạc", color=discord.Color.blurple())
            embed.description = "Hàng chờ trống."
            await queue_message.edit(embed=embed)
        except discord.NotFound:
            print("Tin nhắn hàng chờ không tồn tại.")
        except discord.Forbidden:
            print("Không có quyền chỉnh sửa tin nhắn hàng chờ.")

    # Gửi tin nhắn thông báo dừng nhạc
    stop_message = await ctx.send("🎵 Phát nhạc đã được dừng và hàng chờ đã được xóa.")
    await asyncio.sleep(5)
    await stop_message.delete()

bot.run(bot_token)