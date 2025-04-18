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
import signal
import win32api
import win32con
import psutil
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math
import pystray
from PIL import Image
import threading
import sys
import ctypes

# Đọc token từ file config.json
with open("token.json", "r") as config_file:
    config = json.load(config_file)

bot_token = config["BOT_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

QUEUE_BACKUP_FILE = "queue_backup.json"

def save_queue_backup():
    """Lưu danh sách phát hiện tại ra file JSON"""
    with open(QUEUE_BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

def load_queue_backup():
    """Nạp lại danh sách phát từ file JSON (nếu có)"""
    global queue
    if os.path.exists(QUEUE_BACKUP_FILE):
        with open(QUEUE_BACKUP_FILE, "r", encoding="utf-8") as f:
            try:
                queue = json.load(f)
            except Exception:
                queue = []
        # Xoá file sau khi nạp để tránh phát lại nhiều lần
        os.remove(QUEUE_BACKUP_FILE)

queue = []  # Danh sách hàng chờ
load_queue_backup()  # Nạp lại queue nếu có
is_playing = False  # Trạng thái đang phát nhạc
current_song = None  # Bài nhạc đang phát
is_paused = False  # Trạng thái tạm dừng
queue_message = None  # Tin nhắn embed hiển thị hàng chờ
ffplay_process = None  # Process của ffplay để điều khiển pause/resume

# Thêm cache cho video và playlist
VIDEO_CACHE = {}
PLAYLIST_CACHE = {}
CACHE_DURATION = 3600  # 1 giờ

# Add after VIDEO_CACHE definition
PREFETCH_CACHE = {}  # Cache for prefetched songs

async def prefetch_next_song():
    """Prefetch and cache the next song in queue"""
    if len(queue) > 1:
        next_song = queue[1]
        next_url = next_song["url"]
        
        # Skip if already in cache
        if next_url in VIDEO_CACHE:
            cache_time, _ = VIDEO_CACHE[next_url]
            if time.time() - cache_time < CACHE_DURATION:
                return

        # Prefetch in background
        try:
            await asyncio.get_event_loop().run_in_executor(None, 
                lambda: get_video_info(next_url))
        except Exception as e:
            print(f"Error prefetching next song: {e}")

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
    """Lấy danh sách video từ playlist với cache"""
    if playlist_url in PLAYLIST_CACHE:
        cache_time, videos = PLAYLIST_CACHE[playlist_url]
        if time.time() - cache_time < CACHE_DURATION:
            return videos

    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "extract_flat": "in_playlist",
        "prefer_insecure": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "ignoreerrors": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            if "entries" in playlist_info:
                videos = []
                for video in playlist_info["entries"]:
                    if video:
                        try:
                            video_url = video.get("webpage_url") or video.get("url", "")
                            videos.append({
                                "title": video.get("title", "Unknown Title"),
                                "url": video_url
                            })
                        except Exception as e:
                            continue
                PLAYLIST_CACHE[playlist_url] = (time.time(), videos)
                return videos
    except Exception as e:
        print(f"Lỗi lấy playlist: {e}")
    return []

def get_video_info(url):
    """Lấy thông tin video với cache"""
    if url in VIDEO_CACHE:
        cache_time, info = VIDEO_CACHE[url]
        if time.time() - cache_time < CACHE_DURATION:
            return info

    ydl_opts = {
        "quiet": True,
        "format": "bestaudio",
        "extract_flat": False,
        "force_generic_extractor": False,
        "no_warnings": True,
        "no_check_certificate": True,
        "prefer_insecure": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "ignoreerrors": True,
        "logtostderr": False,
        "default_search": "ytsearch"
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            video_info = {
                "title": info.get("title", "Unknown Title"),
                "duration": info.get("duration", 0),
                "url": info.get("webpage_url", url),
                "thumbnail": info.get("thumbnail") or (info.get("thumbnails", [{}])[0].get("url"))
            }
            VIDEO_CACHE[url] = (time.time(), video_info)
            return video_info
        except Exception as e:
            print(f"Lỗi lấy thông tin video: {e}")
            return {"title": "Unknown Title", "duration": 0, "url": url, "thumbnail": None}

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
        yt_dlp_proc = subprocess.Popen(
            yt_dlp_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            creationflags=subprocess.CREATE_NO_WINDOW  # Ẩn cửa sổ console
        )
        ffplay_proc = subprocess.Popen(
            ffplay_cmd, 
            stdin=yt_dlp_proc.stdout, 
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        # Đợi quá trình ffplay hoàn thành
        ffplay_proc.wait()

        # Đóng yt-dlp
        yt_dlp_proc.terminate()

    except Exception as e:
        print(f"Lỗi khi phát nhạc: {e}")


async def play_next(ctx):
    """Phát bài tiếp theo trong hàng chờ."""
    global is_playing, queue, current_song, queue_message, ffplay_process, is_paused

    if not queue:
        is_playing = False
        current_song = None
        await update_queue_message(ctx)
        return

    # Reset states
    is_paused = False
    is_playing = True
    current_song = queue[0]
    
    # Start prefetching next song
    asyncio.create_task(prefetch_next_song())

    # Stop old process
    if ffplay_process:
        try:
            ffplay_process.terminate()
            ffplay_process.wait()
        except:
            pass
        finally:
            ffplay_process = None

    await update_queue_message(ctx)

    url = current_song["url"]
    video_info = get_video_info(url)
    
    # Chỉ in thông tin nếu đang playing
    if is_playing:
        print(f"\n\n--------------------------------------------------------------------------")
        print(f"\n🎵 Đang phát: {video_info['title']}")
        print(f"🕒 Tổng thời lượng: {str(datetime.timedelta(seconds=video_info['duration']))}")

    def play_song():
        """Chạy yt-dlp và ffplay để phát nhạc."""
        global ffplay_process
        
        try:
            yt_dlp_cmd = [
                "yt-dlp",
                "-f", "bestaudio",
                "--extract-audio",
                "--audio-quality", "0", 
                "--quiet",
                "--no-warnings",
                "--no-check-certificate",
                "--prefer-insecure",
                "--output", "-",
                url
            ]
            ffplay_cmd = [
                "ffplay",
                "-nodisp",
                "-autoexit",
                "-i", "pipe:0",
                "-loglevel", "quiet"
            ]

            yt_dlp_proc = subprocess.Popen(
                yt_dlp_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            ffplay_process = subprocess.Popen(
                ffplay_cmd,
                stdin=yt_dlp_proc.stdout,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            yt_dlp_proc.stdout.close()
            ffplay_process.wait()
            
            if is_playing and ffplay_process and ffplay_process.returncode == 0:
                asyncio.run_coroutine_threadsafe(finish_song(ctx), bot.loop)
            
        except Exception as e:
            print(f"Lỗi phát nhạc (bỏ qua): {e}")

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

def get_current_system_volume():
    """Lấy âm lượng hiện tại của hệ thống (0.0 - 1.0)"""
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        min_db, max_db, _ = volume.GetVolumeRange()
        current_db = volume.GetMasterVolumeLevel()
        # Chuyển dB về 0.0 - 1.0
        return (current_db - min_db) / (max_db - min_db)
    except Exception as e:
        print(f"Lỗi lấy âm lượng hệ thống: {e}")
        return 0.5  # fallback

def set_application_volume(volume_level):
    """Điều chỉnh âm lượng của ứng dụng ffplay"""
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        min_db, max_db, _ = volume.GetVolumeRange()
        volume_db = min_db + (max_db - min_db) * volume_level
        volume.SetMasterVolumeLevel(volume_db, None)
        return True
    except Exception as e:
        print(f"Lỗi điều chỉnh âm lượng: {e}")
        return False

# Fix AddSongModal to use a fallback for TextInput
class AddSongModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Thêm bài hát")
        self.view = view
        # Try to use TextInput from discord.ui, fallback to InputText if needed
        try:
            TextInput = discord.ui.TextInput
        except AttributeError:
            # Fallback for very old discord.py versions (rare)
            from discord.ui.input_text import InputText as TextInput
        self.song_input = TextInput(
            label="Nhập tên bài hát hoặc URL",
            placeholder="Nhập tên bài hát, URL YouTube hoặc URL playlist...",
            min_length=2,
            max_length=200,
            required=True,
        )
        self.add_item(self.song_input)

    async def on_submit(self, interaction):
        await interaction.response.defer()
        query = str(self.song_input.value)
        ctx = self.view.ctx

        status_message = await ctx.send(embed=discord.Embed(
            title="🔍 Đang xử lý...",
            description=f"**{query}**",
            color=discord.Color.blue()
        ))

        # Tìm kiếm video/playlist
        result = await search_youtube_song(query)

        if not result:
            error_embed = discord.Embed(
                title="❌ Không tìm thấy!",
                description=f"Không tìm thấy nội dung nào khớp với: **{query}**",
                color=discord.Color.red()
            )
            await status_message.edit(embed=error_embed)
            await asyncio.sleep(5)
            await status_message.delete()
            return

        if result['type'] == 'playlist':
            videos = result['videos']
            queue.extend({"title": video['title'], "url": video['url']} for video in videos)
            success_embed = discord.Embed(
                title="✅ Đã thêm playlist!",
                description="\n".join(
                    f"**[{video['title']}]({video['url']})**" for video in videos[:10]
                ) + (f"\n...và {len(videos)-10} bài nữa" if len(videos) > 10 else ""),
                color=discord.Color.green()
            )
        else:
            video = result['video']
            queue.append({
                "title": video['title'],
                "url": video['url']
            })
            success_embed = discord.Embed(
                title="✅ Đã thêm vào hàng chờ!",
                description=f"**[{video['title']}]({video['url']})**",
                color=discord.Color.green()
            )

        success_embed.set_footer(text=f"Yêu cầu bởi: {interaction.user}")
        await status_message.edit(embed=success_embed)
        await update_queue_message(ctx)

        if not is_playing:
            await play_next(ctx)

        await asyncio.sleep(5)
        await status_message.delete()

class RemoveSongSelect(discord.ui.Select):
    def __init__(self, ctx, queue):
        options = []
        # Bỏ qua bài đang phát (index 0)
        for i, song in enumerate(queue[1:11], start=1):
            title = song['title'] if isinstance(song, dict) else str(song)
            options.append(discord.SelectOption(label=f"{i}. {title}", value=str(i)))
        super().__init__(placeholder="🗑️ Xoá bài khỏi hàng chờ...", min_values=1, max_values=1, options=options)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        idx = int(self.values[0])
        # Xoá bài khỏi queue (idx là vị trí trong queue, đã bỏ qua bài đầu)
        try:
            removed = queue.pop(idx)
            info = get_video_info(removed['url'])
            await interaction.response.send_message(
                f"🗑️ Đã xoá **[{info['title']}]({info.get('url', removed['url'])})** khỏi hàng chờ.", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message("❌ Không thể xoá bài!", ephemeral=True)

class QueueControlView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

        # Thêm nút Add Song (➕)
        add_button = discord.ui.Button(label="➕", style=discord.ButtonStyle.secondary)
        add_button.callback = self.add_song_callback
        self.add_item(add_button)

        # Tạo nút Stop (🛑)
        stop_button = discord.ui.Button(label="🛑", style=discord.ButtonStyle.secondary)
        stop_button.callback = self.stop_callback
        self.add_item(stop_button)  # Thêm nút vào View

        # Tạo nút Skip (⏭️)
        skip_button = discord.ui.Button(label="⏭️", style=discord.ButtonStyle.secondary)
        skip_button.callback = self.skip_callback
        self.add_item(skip_button)  # Thêm nút vào View

        # Tạo nút Pause/Resume (⏯️)
        pause_button = discord.ui.Button(label="⏯️", style=discord.ButtonStyle.secondary)
        pause_button.callback = self.pause_callback
        self.add_item(pause_button)

        # Thêm nút Replay (🔁)
        replay_button = discord.ui.Button(label="🔁", style=discord.ButtonStyle.secondary)
        replay_button.callback = self.replay_callback
        self.add_item(replay_button)

        # Thêm nút âm lượng
        volume_down = discord.ui.Button(label="🔉", style=discord.ButtonStyle.secondary)
        volume_down.callback = self.volume_down_callback
        self.add_item(volume_down)

        volume_up = discord.ui.Button(label="🔊", style=discord.ButtonStyle.secondary)
        volume_up.callback = self.volume_up_callback
        self.add_item(volume_up)

        if len(queue) > 1:
            self.add_item(RemoveSongSelect(ctx, queue))

    async def stop_callback(self, interaction: discord.Interaction):
        """
        Xử lý khi người dùng nhấn nút 🛑 (Stop).
        """
        await interaction.response.defer()

        global is_playing, queue, current_song
        is_playing = False
        queue.clear()
        current_song = None

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        subprocess.run(
            ["taskkill", "/IM", "ffplay.exe", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo
        )


        queue_message_id = load_queue_message_id()
        if queue_message_id:
            try:
                queue_message = await self.ctx.fetch_message(queue_message_id)  # Sửa ở đây
                embed = discord.Embed(title="🎵 Hàng chờ phát nhạc", color=discord.Color.blurple())
                embed.description = "Hàng chờ trống."
                await queue_message.edit(embed=embed, view=self)
            except discord.NotFound:
                pass

    async def skip_callback(self, interaction: discord.Interaction):
        """Xử lý khi người dùng nhấn nút ⏭️ (Skip)."""
        await interaction.response.defer()
        global is_playing, queue, current_song, ffplay_process

        if not is_playing or not queue:
            return
        
        if len(queue) == 1:
            return

        try:
            if ffplay_process:
                ffplay_process.terminate()
                ffplay_process.wait(timeout=2)
        except:
            pass
        finally:
            ffplay_process = None

        queue.pop(0)
        await play_next(self.ctx)

    async def pause_callback(self, interaction: discord.Interaction):
        global is_paused, ffplay_process

        await interaction.response.defer()

        if not is_playing or not ffplay_process:
            return

        try:
            if is_paused:
                psutil.Process(ffplay_process.pid).resume()
                is_paused = False
            else:
                psutil.Process(ffplay_process.pid).suspend()
                is_paused = True
        except:
            pass

        # Cập nhật lại embed để hiển thị trạng thái (Tạm dừng)
        await update_queue_message(self.ctx)

    async def volume_up_callback(self, interaction: discord.Interaction):
        """Tăng âm lượng"""
        await interaction.response.defer()
        if not is_playing:
            return
        current = get_current_system_volume()
        new_volume = min(1.0, current + 0.05)
        set_application_volume(new_volume)

    async def volume_down_callback(self, interaction: discord.Interaction):
        """Giảm âm lượng"""
        await interaction.response.defer()
        if not is_playing:
            return
        current = get_current_system_volume()
        new_volume = max(0.0, current - 0.05)
        set_application_volume(new_volume)

    async def add_song_callback(self, interaction: discord.Interaction):
        """Xử lý khi người dùng nhấn nút Add Song"""
        add_modal = AddSongModal(self)
        try:
            await interaction.response.send_modal(add_modal)
        except discord.NotFound:
            try:
                await interaction.followup.send(
                    "❌ Nút này đã hết hạn hoặc không còn hiệu lực. Vui lòng tải lại hàng chờ và thử lại.",
                    ephemeral=True
                )
            except Exception:
                pass
    
    async def replay_callback(self, interaction: discord.Interaction):
        """Phát lại bài hát hiện tại."""
        await interaction.response.defer()
        global is_playing, ffplay_process

        if not is_playing or not queue:
            return

        # Dừng ffplay hiện tại nếu còn
        if ffplay_process:
            try:
                ffplay_process.terminate()
                ffplay_process.wait(timeout=2)
            except:
                pass
            finally:
                ffplay_process = None

        # Phát lại bài đầu queue (bài hiện tại)
        await play_next(self.ctx)

async def update_queue_message(ctx):
    global queue_message_id, queue, current_song, is_paused

    active_channel_id = load_active_channel_id()
    # Hỗ trợ cả Context và TextChannel
    channel_id = getattr(ctx, "channel", ctx).id if hasattr(ctx, "channel") else ctx.id
    if active_channel_id and channel_id != active_channel_id:
        return

    queue_message_id = load_queue_message_id()

    queue_message = None
    # Lấy channel object đúng kiểu
    channel = ctx.channel if hasattr(ctx, "channel") else ctx
    if queue_message_id:
        try:
            queue_message = await channel.fetch_message(queue_message_id)
        except discord.NotFound:
            queue_message = None

    # Thay đổi tiêu đề nếu đang tạm dừng
    embed_title = "🎵 Hàng chờ phát nhạc"
    if is_paused:
        embed_title += " (Tạm dừng)"

    embed = discord.Embed(title=embed_title, color=discord.Color.blurple())

    if not queue:
        embed.description = "Hàng chờ trống."
    else:
        try:
            current_song_info = get_video_info(queue[0]['url'])
            current_title = current_song_info['title']
            current_url = current_song_info.get('url', queue[0]['url'])
            embed.description = f"**Đang phát: [{current_title}]({current_url})**\n\n"
            # Thêm thumbnail
            if current_song_info.get("thumbnail"):
                embed.set_thumbnail(url=current_song_info["thumbnail"])

            next_songs = queue[1:11]
            if next_songs:
                embed.description += "**Tiếp theo:**\n"
                for i, song in enumerate(next_songs):
                    info = get_video_info(song['url'])
                    title = info['title']
                    url = info.get('url', song['url'])
                    embed.description += f"  **#{i + 1}:** [{title}]({url})\n"

            # Tính tổng thời lượng hàng chờ
            total_duration = 0
            for song in queue:
                info = get_video_info(song['url'])
                total_duration += info.get('duration', 0)
            formatted_duration = str(datetime.timedelta(seconds=total_duration))

            embed.set_footer(
                text=f"📊 Tổng số bài trong hàng chờ: {len(queue)}  | ⏳ Thời lượng ước tính: {formatted_duration}"
            )
        except Exception as e:
            print(f"Lỗi cập nhật embed: {e}")
            embed.description = "Lỗi hiển thị hàng chờ"

    if not queue_message:
        queue_message = await channel.send(embed=embed, view=QueueControlView(channel))
        queue_message_id = queue_message.id
        save_queue_message_id(queue_message_id)
    else:
        await queue_message.edit(embed=embed, view=QueueControlView(channel))

async def clear_queue_message(ctx):
    """Cập nhật tin nhắn hàng chờ thành trống"""
    active_channel_id = load_active_channel_id()
    # Sửa ở đây: ctx có thể là Context hoặc TextChannel
    channel_id = getattr(ctx, "channel", ctx).id if hasattr(ctx, "channel") else ctx.id
    if active_channel_id and channel_id != active_channel_id:
        return
    queue_message_id = load_queue_message_id()
    if queue_message_id:
        try:
            # ctx có thể là Context hoặc TextChannel
            channel = ctx.channel if hasattr(ctx, "channel") else ctx
            queue_message = await channel.fetch_message(queue_message_id)
            embed = discord.Embed(title="🎵 Hàng chờ phát nhạc", color=discord.Color.blurple())
            embed.description = "Hàng chờ trống."
            await queue_message.edit(embed=embed)
        except:
            pass

def cleanup_processes():
    """Dọn dẹp tất cả các process khi tắt chương trình"""
    global is_playing, queue, current_song
    
    # Đặt lại các trạng thái
    is_playing = False
    queue.clear()
    current_song = None

    # Tắt ffplay
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(
            ["taskkill", "/IM", "ffplay.exe", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo
        )
    except:
        pass
    
    # Tắt các process khác nếu có
    if ffplay_process:
        try:
            ffplay_process.terminate()
            ffplay_process.wait(timeout=2)
        except:
            pass

    # Cập nhật tin nhắn hàng chờ thành trống nếu có thể
    if bot.is_ready():
        for guild in bot.guilds:
            # Tìm kênh text đầu tiên có thể gửi tin nhắn
            text_channel = next((channel for channel in guild.text_channels 
                               if channel.permissions_for(guild.me).send_messages), None)
            if text_channel:
                asyncio.run_coroutine_threadsafe(
                    clear_queue_message(text_channel), 
                    bot.loop
                ).result(timeout=5)

def create_tray_icon():
    """Tạo và hiển thị tray icon"""

    def on_exit(icon):
        icon.stop()
        cleanup_processes()
        asyncio.run_coroutine_threadsafe(bot.close(), bot.loop)
        os._exit(0)

    def on_save_and_exit(icon, item):
        save_queue_backup()
        icon.stop()
        cleanup_processes()
        asyncio.run_coroutine_threadsafe(bot.close(), bot.loop)
        os._exit(0)

    menu = pystray.Menu(
        pystray.MenuItem("Lưu danh sách phát và Thoát", on_save_and_exit),
        pystray.MenuItem("THOÁT", on_exit)
    )

    try:
        image = Image.open("icon.png")
    except:
        image = Image.new('RGB', (64, 64), color='blue')

    icon = pystray.Icon(
        "music_bot",
        image,
        "Discord Music Bot",
        menu
    )

    icon.run()

@bot.event
async def on_ready():
    ctypes.windll.user32.MessageBoxW(
        0,
        f"Bot đã khởi động với tên: {bot.user}",
        str(bot.user),  # Đặt tiêu đề hộp thoại là tên bot
        0x40
    )
    print(f"Bot đã sẵn sàng! Đăng nhập với tên: {bot.user}")
    threading.Thread(target=create_tray_icon, daemon=True).start()
    active_channel_id = load_active_channel_id()
    for guild in bot.guilds:
        text_channel = None
        if active_channel_id:
            text_channel = discord.utils.get(guild.text_channels, id=active_channel_id)
        if not text_channel:
            text_channel = next((channel for channel in guild.text_channels 
                                 if channel.permissions_for(guild.me).send_messages), None)
        if text_channel:
            queue_message_id = load_queue_message_id()
            queue_message = None
            if queue_message_id:
                try:
                    queue_message = await text_channel.fetch_message(queue_message_id)
                except discord.NotFound:
                    queue_message = None

            # Tạo embed mới
            embed_title = "🎵 Hàng chờ phát nhạc"
            embed = discord.Embed(title=embed_title, color=discord.Color.blurple())
            if not queue:
                embed.description = "Hàng chờ trống."
            else:
                try:
                    # Hiển thị bài đang phát là link
                    current_song_info = get_video_info(queue[0]['url'])
                    current_title = current_song_info['title']
                    current_url = current_song_info.get('url', queue[0]['url'])
                    embed.description = f"**Đang phát: [{current_title}]({current_url})**\n\n"
                    # Thêm thumbnail nếu có
                    if current_song_info.get("thumbnail"):
                        embed.set_thumbnail(url=current_song_info["thumbnail"])
                    # Danh sách tiếp theo
                    next_songs = queue[1:11]
                    if next_songs:
                        embed.description += "**Tiếp theo:**\n"
                        for i, song in enumerate(next_songs):
                            info = get_video_info(song['url'])
                            title = info['title']
                            url = info.get('url', song['url'])
                            embed.description += f"  **#{i + 1}:** [{title}]({url})\n"
                    # Tổng thời lượng
                    total_duration = 0
                    for song in queue:
                        info = get_video_info(song['url'])
                        total_duration += info.get('duration', 0)
                    formatted_duration = str(datetime.timedelta(seconds=total_duration))
                    embed.set_footer(
                        text=f"📊 Tổng số bài trong hàng chờ: {len(queue)}  | ⏳ Thời lượng ước tính: {formatted_duration}"
                    )
                except Exception as e:
                    print(f"Lỗi cập nhật embed: {e}")
                    embed.description = "Lỗi hiển thị hàng chờ"
            if not queue_message:
                queue_message = await text_channel.send(embed=embed, view=QueueControlView(text_channel))
                save_queue_message_id(queue_message.id)
            else:
                await queue_message.edit(embed=embed, view=QueueControlView(text_channel))

    # Tự động phát tiếp nếu có queue đã lưu
    if queue and not is_playing:
        await play_next(text_channel)
        

import asyncio
import datetime
import discord
import yt_dlp
from discord.ext import commands

async def search_youtube_song(query: str):
    """Helper function để tìm kiếm video trên YouTube"""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True, 
        "default_search": "ytsearch",
        "format": "bestaudio"
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Check if it's a playlist first
            if "playlist" in query:
                info = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ydl.extract_info(query, download=False))
                if info and 'entries' in info:
                    # Return all videos in playlist
                    videos = []
                    for entry in info['entries']:
                        if entry:
                            videos.append({
                                'title': entry.get('title', 'Unknown Title'),
                                'url': entry.get('webpage_url', entry.get('url', '')),
                                'duration': entry.get('duration', 0)
                            })
                    return {'type': 'playlist', 'videos': videos}

            # If not playlist, handle as single video
            if query.startswith(('http://', 'https://')):
                info = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ydl.extract_info(query, download=False))
            else:
                info = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ydl.extract_info(f"ytsearch:{query}", download=False))
            
            if info is None:
                return None
                
            if 'entries' in info:
                video = info['entries'][0]
            else:
                video = info
            
            return {
                'type': 'video',
                'video': {
                    'title': video.get('title', 'Unknown Title'),
                    'url': video.get('webpage_url', video.get('url', '')),
                    'duration': video.get('duration', 0)
                }
            }
    except Exception as e:
        print(f"Lỗi tìm kiếm video: {e}")
        return None

ACTIVE_CHANNEL_FILE = "active_channel.json"

def save_active_channel_id(channel_id):
    """Lưu ID kênh mặc định vào file JSON"""
    with open(ACTIVE_CHANNEL_FILE, "w") as file:
        json.dump({"active_channel_id": channel_id}, file)

def load_active_channel_id():
    """Đọc ID kênh mặc định từ file JSON"""
    if os.path.exists(ACTIVE_CHANNEL_FILE):
        with open(ACTIVE_CHANNEL_FILE, "r") as file:
            data = json.load(file)
            return data.get("active_channel_id")
    return None

def is_active_channel(ctx):
    """Kiểm tra xem ctx.channel có phải là kênh mặc định không"""
    active_channel_id = load_active_channel_id()
    return active_channel_id is None or ctx.channel.id == active_channel_id

@bot.command(name="activate")
async def activate(ctx):
    """Đặt kênh hiện tại thành kênh mặc định của bot"""
    save_active_channel_id(ctx.channel.id)
    embed = discord.Embed(
        title="✅ Đã đặt kênh mặc định!",
        description=f"Bot sẽ chỉ gửi tin nhắn tại kênh này: {ctx.channel.mention}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="play")
async def play(ctx, *, query: str = None):
    """Nhận lệnh từ Discord, tìm video hoặc phát nhạc."""
    if not is_active_channel(ctx):
        return
    if query is None:
        help_embed = discord.Embed(
            title="❓ Hướng dẫn sử dụng lệnh play",
            description="**Cách dùng:**\n"
                      "`.play <tên bài hát hoặc URL>`\n\n"
                      "**Ví dụ:**\n"
                      "`.play never gonna give you up`\n"
                      "`.play https://www.youtube.com/watch?v=dQw4w9WgXcQ`\n"
                      "`.play https://youtube.com/playlist?list=...`",
            color=discord.Color.blue()
        )
        help_message = await ctx.send(embed=help_embed)
        await asyncio.sleep(10)
        await help_message.delete()
        return

    global queue, is_playing
    request_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await ctx.message.delete()

    status_message = await ctx.send(embed=discord.Embed(
        title="🔍 Đang xử lý...", 
        description=f"**{query}**",
        color=discord.Color.blue()
    ))

    # Tìm kiếm video/playlist
    result = await search_youtube_song(query)
    
    if not result:
        error_embed = discord.Embed(
            title="❌ Không tìm thấy!",
            description=f"Không tìm thấy nội dung nào khớp với: **{query}**",
            color=discord.Color.red()
        )
        await status_message.edit(embed=error_embed)
        await asyncio.sleep(5)
        await status_message.delete()
        return

    if result['type'] == 'playlist':
        videos = result['videos']
        queue.extend({"title": video['title'], "url": video['url']} for video in videos)
        success_embed = discord.Embed(
            title="✅ Đã thêm playlist!",
            description="\n".join(
                f"**[{video['title']}]({video['url']})**" for video in videos[:10]
            ) + (f"\n...và {len(videos)-10} bài nữa" if len(videos) > 10 else ""),
            color=discord.Color.green()
        )
    else:
        video = result['video']
        queue.append({
            "title": video['title'],
            "url": video['url']
        })
        success_embed = discord.Embed(
            title="✅ Đã thêm vào hàng chờ!",
            description=f"**[{video['title']}]({video['url']})**",
            color=discord.Color.green()
        )

    success_embed.set_footer(text=f"Yêu cầu bởi: {ctx.author} | {request_time}")
    await status_message.edit(embed=success_embed)
    await update_queue_message(ctx)

    if not is_playing:
        await play_next(ctx)

    await asyncio.sleep(5)
    await status_message.delete()

@bot.command(name="p")
async def p(ctx, *, query: str = None):
    """Alias cho lệnh play"""
    if not is_active_channel(ctx):
        return
    if query is None:
        help_embed = discord.Embed(
            title="❓ Hướng dẫn sử dụng lệnh p",
            description="**Cách dùng:**\n"
                      "`.p <tên bài hát hoặc URL>`\n\n"
                      "**Ví dụ:**\n"
                      "`.p never gonna give you up`\n"
                      "`.p https://www.youtube.com/watch?v=dQw4w9WgXcQ`\n"
                      "`.p https://youtube.com/playlist?list=...`",
            color=discord.Color.blue()
        )
        help_message = await ctx.send(embed=help_embed)
        await asyncio.sleep(10)
        await help_message.delete()
        return

    await play(ctx, query=query)

@bot.command(name="skip")
async def skip(ctx):
    """Bỏ qua bài hát hiện tại."""
    if not is_active_channel(ctx):
        return
    global is_playing, queue, current_song, ffplay_process
    await ctx.message.delete()

    if not is_playing or not queue:
        skip_message = await ctx.send("🎵 Không có bài hát nào đang phát để bỏ qua.")
        await asyncio.sleep(5)
        await skip_message.delete()
        return

    # Kiểm tra nếu đây là bài cuối cùng
    if len(queue) == 1:
        skip_message = await ctx.send("🎵 Đây là bài hát cuối cùng trong hàng chờ.")
        await asyncio.sleep(5)
        await skip_message.delete()
        return

    # Dừng bài đang phát
    if ffplay_process:
        try:
            ffplay_process.terminate()
            ffplay_process.wait()
        except:
            pass
        finally:
            ffplay_process = None

    # Bắt đầu chuyển bài
    
    queue.pop(0)
    await play_next(ctx)


@bot.command(name="stop")
async def stop(ctx):
    """
    Dừng phát nhạc.
    """
    if not is_active_channel(ctx):
        return
    global is_playing, queue, current_song
    is_playing = False
    queue.clear()
    current_song = None

    # Gửi lệnh dừng tới ffplay
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    subprocess.run(
        ["taskkill", "/IM", "ffplay.exe", "/F"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        startupinfo=startupinfo
    )


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

@bot.command(name="pause")
async def pause_command(ctx):
    """
    Tạm dừng/tiếp tục phát nhạc hiện tại.
    """
    if not is_active_channel(ctx):
        return
    global is_paused, ffplay_process

    await ctx.message.delete()

    if not is_playing or not ffplay_process:
        pause_message = await ctx.send("🎵 Không có bài hát nào đang phát.")
        await asyncio.sleep(5)
        await pause_message.delete()
        return

    if is_paused:
        try:
            psutil.Process(ffplay_process.pid).resume()
            is_paused = False
            pause_message = await ctx.send("▶️ Đã tiếp tục phát nhạc.")
        except:
            pause_message = await ctx.send("❌ Không thể tiếp tục phát nhạc.")
    else:
        try:
            psutil.Process(ffplay_process.pid).suspend()
            is_paused = True
            pause_message = await ctx.send("⏸️ Đã tạm dừng phát nhạc.")
        except:
            pause_message = await ctx.send("❌ Không thể tạm dừng phát nhạc.")

    # Cập nhật lại embed để hiển thị trạng thái (Tạm dừng)
    await update_queue_message(ctx)

    await asyncio.sleep(5)
    await pause_message.delete()

@bot.command(name="h")
async def help_command(ctx):
    """Hiển thị hướng dẫn sử dụng bot và các lệnh"""
    try:
        await ctx.message.delete()
    except discord.NotFound:
        pass
    help_text = (
        "**HƯỚNG DẪN SỬ DỤNG BOT NHẠC**\n\n"
        "Các lệnh chính:\n"
        "• `!play <tên bài hát hoặc URL>`: Thêm bài hát hoặc playlist vào hàng chờ\n"
        "• `!p <tên bài hát hoặc URL>`: Alias cho !play\n"
        "• `!skip`: Bỏ qua bài hát hiện tại\n"
        "• `!stop`: Dừng phát nhạc và xoá hàng chờ\n"
        "• `!pause`: Tạm dừng/tiếp tục phát nhạc\n"
        "• `!activate`: Đặt kênh hiện tại làm kênh mặc định của bot\n"
        "• `!h`: Hiển thị hướng dẫn này\n\n"
        "**Hướng dẫn sử dụng các nút trên embed:**\n"
        "- ⏭️ Skip: Bỏ qua bài hát hiện tại\n"
        "- 🛑 Stop: Dừng phát nhạc và xoá hàng chờ\n"
        "- ⏯️ Pause/Resume: Tạm dừng hoặc tiếp tục phát nhạc\n"
        "- ➕ Add Song: Thêm bài hát mới vào hàng chờ\n"
        "- 🔉 Giảm âm lượng | 🔊 Tăng âm lượng\n"
        "\nChỉ hoạt động tại kênh mặc định (sau khi dùng !activate). Nếu gặp lỗi hoặc không rõ lệnh, hãy dùng `!h` để xem hướng dẫn."
    )
    embed = discord.Embed(
        title="🎵 Hướng dẫn sử dụng bot nhạc",
        description=help_text,
        color=discord.Color.blurple()
    )
    message = await ctx.send(embed=embed)
    await asyncio.sleep(30)
    try:
        await message.delete()
    except discord.NotFound:
        pass

@bot.event
async def on_message(message):
    # Bỏ qua tin nhắn của bot
    if message.author.bot:
        return

    active_channel_id = load_active_channel_id()
    # Nếu không có kênh mặc định, xử lý bình thường
    if not active_channel_id or message.channel.id != active_channel_id:
        await bot.process_commands(message)
        return

    # Xoá tin nhắn ngay sau khi gửi (trừ lệnh !activate để tránh tự xoá khi cài đặt)
    if message.content.strip().startswith("!activate"):
        await bot.process_commands(message)
        try:
            await message.delete()
        except discord.NotFound:
            pass
        return

    # Kiểm tra nếu là lệnh hợp lệ
    ctx = await bot.get_context(message)
    if ctx.valid:
        await bot.process_commands(message)
        try:
            await message.delete()
        except discord.NotFound:
            pass
        return

    # Nếu là lệnh nhưng không hợp lệ (bắt đầu bằng ! nhưng không đúng lệnh)
    if message.content.strip().startswith("!"):
        try:
            await message.delete()
        except discord.NotFound:
            pass
        reply = await message.channel.send(
            f"❌ Lệnh không hợp lệ. Dùng `!h` để xem hướng dẫn sử dụng bot."
        )
        await asyncio.sleep(5)
        await reply.delete()
        return

    # Nếu không phải lệnh
    try:
        await message.delete()
    except discord.NotFound:
        pass
    reply = await message.channel.send(
        f"❌ Đây không phải lệnh bot. Dùng `!h` để xem hướng dẫn sử dụng bot."
    )
    await asyncio.sleep(5)
    await reply.delete()
    

if __name__ == "__main__":
    try:
        bot.run(bot_token)
    except:
        pass
    finally:
        cleanup_processes()