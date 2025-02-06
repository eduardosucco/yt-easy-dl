import os
import re
import dropbox
import yt_dlp
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def sanitize_title(title):
    """Remove caracteres problemáticos e converte espaços em underscore."""
    import re
    title = re.sub(r'[^\w\s-]', '', title, flags=re.UNICODE)
    title = re.sub(r'[-\s]+', '_', title.strip())
    return title

def download_video(video_url):
    """
    Baixa o vídeo do YouTube usando yt_dlp e retorna o caminho do arquivo.
    O nome do arquivo fica em 'videos/Título_YYYYMMDD_HHMM.ext'.
    """

    # Garante que a pasta 'videos' exista
    os.makedirs('videos', exist_ok=True)

    # Descobre metadados do vídeo (para pegar título)
    with yt_dlp.YoutubeDL() as ydl_info:
        info = ydl_info.extract_info(video_url, download=False)
    raw_title = info.get('title') or 'video_sem_titulo'
    safe_title = sanitize_title(raw_title)

    # Gera timestamp
    now_str = datetime.now().strftime('%Y%m%d_%H%M')
    final_name = f"{safe_title}_{now_str}"  # ex: MeuVideo_20250206_1530
    output_path = f"videos/{final_name}.%(ext)s"

    ffmpeg_bin = "bin/ffmpeg"  # Uso do binário local (sem download dinâmico)
    ydl_opts = {
        'outtmpl': output_path,
        'ffmpeg_location': ffmpeg_bin
    }

    # Baixa o vídeo
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    # Descobre qual extensão foi baixada
    possible_extensions = ["mp4", "mkv", "webm", "m4a", "mp3"]
    for ext in possible_extensions:
        candidate = f"videos/{final_name}.{ext}"
        if os.path.exists(candidate):
            return candidate

    return None

def upload_to_dropbox(file_path):
    """
    Faz upload do arquivo para o Dropbox e retorna o link compartilhável.
    """
    dropbox_token = os.getenv("DROPBOX_ACCESS_TOKEN")
    if not dropbox_token:
        raise ValueError("Faltando DROPBOX_ACCESS_TOKEN (verifique .env ou Streamlit Secrets).")

    dbx = dropbox.Dropbox(dropbox_token)
    dropbox_path = f"/{os.path.basename(file_path)}"

    with open(file_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))

    link_info = dbx.sharing_create_shared_link_with_settings(dropbox_path)
    return link_info.url
