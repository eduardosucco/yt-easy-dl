import os
import dropbox
import yt_dlp
from dotenv import load_dotenv
from datetime import datetime
import re

load_dotenv()

def sanitize_title(title):
    title = re.sub(r'[^\w\s-]', '', title, flags=re.UNICODE)
    title = re.sub(r'[-\s]+', '_', title.strip())
    return title

def get_video_info(video_url):
    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(video_url, download=False)
    return info

def download_video(video_url, download_type="video"):
    """
    Baixa o vídeo (ou áudio) do YouTube usando yt_dlp e retorna o caminho do arquivo resultante.
    download_type pode ser "video" ou "audio".
    """
    ffmpeg_bin = "bin/ffmpeg"

    info = get_video_info(video_url)
    raw_title = info.get("title") or "video_sem_titulo"
    safe_title = sanitize_title(raw_title)

    now_str = datetime.now().strftime("%Y%m%d_%H%M")
    final_name = f"{safe_title}_{now_str}"

    os.makedirs("videos", exist_ok=True)

    # Se for vídeo, usamos outtmpl normal.
    # Se for áudio MP3, passamos postprocessor para extrair MP3.
    if download_type == "audio":
        outtmpl = f"videos/{final_name}.%(ext)s"
        ydl_opts = {
            'outtmpl': outtmpl,
            'ffmpeg_location': ffmpeg_bin,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        expected_extensions = ["mp3"]  # só MP3
    else:
        outtmpl = f"videos/{final_name}.%(ext)s"
        ydl_opts = {
            'outtmpl': outtmpl,
            'ffmpeg_location': ffmpeg_bin,
        }
        expected_extensions = ["mp4", "mkv", "webm"]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    # Descobre a extensão real baixada
    for ext in expected_extensions:
        candidate = f"videos/{final_name}.{ext}"
        if os.path.exists(candidate):
            return candidate
    
    return None

def upload_to_dropbox(file_path):
    dropbox_token = os.getenv("DROPBOX_ACCESS_TOKEN")
    if not dropbox_token:
        raise ValueError("Faltando DROPBOX_ACCESS_TOKEN.")

    dbx = dropbox.Dropbox(dropbox_token)

    # Garante a pasta /streamlit-videos
    folder_name = "/streamlit-videos"
    try:
        dbx.files_create_folder_v2(folder_name)
    except dropbox.exceptions.ApiError as e:
        if "folder_conflict" not in str(e):
            raise e

    dropbox_path = f"{folder_name}/{os.path.basename(file_path)}"
    with open(file_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))

    link_info = dbx.sharing_create_shared_link_with_settings(dropbox_path)
    return link_info.url
