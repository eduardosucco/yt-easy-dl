import os
import re
import dropbox
import yt_dlp
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def sanitize_title(title):
    """
    Remove caracteres que podem dar problema em nomes de arquivo e troca espaços por underscore.
    """
    title = re.sub(r'[^\w\s-]', '', title, flags=re.UNICODE)
    title = re.sub(r'[-\s]+', '_', title.strip())
    return title

def get_video_info(video_url):
    """
    Retorna metadados do vídeo, sem fazer download (thumbnail, título, duração, etc.)
    """
    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(video_url, download=False)
    return info

def download_video(video_url, download_type="video"):
    """
    Baixa o vídeo ou áudio do YouTube usando yt_dlp e retorna o caminho do arquivo.
    download_type: "video" ou "audio"
    """
    ffmpeg_bin = "bin/ffmpeg"  # Caminho do binário ffmpeg no repositório

    # Extrai informações
    info = get_video_info(video_url)
    raw_title = info.get("title", "video_sem_titulo")
    safe_title = sanitize_title(raw_title)

    # Cria pasta local para salvar
    os.makedirs("videos", exist_ok=True)
    now_str = datetime.now().strftime("%Y%m%d_%H%M")
    final_name = f"{safe_title}_{now_str}"

    if download_type == "audio":
        # Baixar só áudio e converter para MP3
        ydl_opts = {
            'outtmpl': f'videos/{final_name}.%(ext)s',
            'ffmpeg_location': ffmpeg_bin,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        expected_extensions = ["mp3"]
    else:
        # Baixar o vídeo
        ydl_opts = {
            'outtmpl': f'videos/{final_name}.%(ext)s',
            'ffmpeg_location': ffmpeg_bin,
        }
        expected_extensions = ["mp4", "mkv", "webm"]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    # Descobrir qual extensão foi salva
    for ext in expected_extensions:
        candidate = f"videos/{final_name}.{ext}"
        if os.path.exists(candidate):
            return candidate

    return None

def upload_to_dropbox(file_path):
    """
    Faz upload do arquivo para a pasta /streamlit-videos no Dropbox e retorna um link compartilhável.
    Substitua "?dl=0" por "?dl=1" para forçar download.
    """
    dropbox_token = os.getenv("DROPBOX_ACCESS_TOKEN")
    if not dropbox_token:
        raise ValueError("DROPBOX_ACCESS_TOKEN não encontrado. Verifique seu .env ou Secrets.")

    dbx = dropbox.Dropbox(dropbox_token)

    # Garante a pasta /streamlit-videos
    folder_name = "/streamlit-videos"
    try:
        dbx.files_create_folder_v2(folder_name)
    except dropbox.exceptions.ApiError as e:
        # Se já existe, ignora o erro
        if "folder_conflict" not in str(e):
            raise e

    # Caminho no Dropbox
    dropbox_path = f"{folder_name}/{os.path.basename(file_path)}"

    with open(file_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))

    link_info = dbx.sharing_create_shared_link_with_settings(dropbox_path)
    return link_info.url
