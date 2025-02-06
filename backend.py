import os
import dropbox
import yt_dlp
from dotenv import load_dotenv
from datetime import datetime
import re

load_dotenv()

def create_dropbox_folder(dbx, folder_name="/streamlit-videos"):
    """
    Cria a pasta no Dropbox, se ainda não existir.
    """
    from dropbox.exceptions import ApiError
    try:
        dbx.files_create_folder_v2(folder_name)
    except ApiError as e:
        # Se a pasta já existe, ignoramos o erro
        if "folder_conflict" in str(e):
            pass
        else:
            raise e

def upload_to_dropbox(file_path):
    """
    Faz upload do arquivo para a pasta /streamlit-videos no Dropbox e retorna um link compartilhável.
    """
    dropbox_token = os.getenv("DROPBOX_ACCESS_TOKEN")
    if not dropbox_token:
        raise ValueError("Faltando DROPBOX_ACCESS_TOKEN (verifique .env ou Streamlit Secrets).")

    dbx = dropbox.Dropbox(dropbox_token)

    # Cria/garante que a pasta streamlit-videos existe
    create_dropbox_folder(dbx, "/streamlit-videos")

    # Caminho de destino no Dropbox
    dropbox_path = f"/streamlit-videos/{os.path.basename(file_path)}"

    with open(file_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))

    link_info = dbx.sharing_create_shared_link_with_settings(dropbox_path)
    return link_info.url

def sanitize_title(title):
    """
    Remove caracteres que podem causar problemas em nomes de arquivo
    e substitui espaços por underscores.
    """
    title = re.sub(r'[^\w\s-]', '', title, flags=re.UNICODE)
    title = re.sub(r'[-\s]+', '_', title.strip())
    return title

def get_video_info(video_url):
    """
    Retorna o dicionário de metadados do vídeo (sem baixar).
    """
    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(video_url, download=False)
    return info

def download_video(video_url):
    """
    Baixa o vídeo usando yt_dlp e retorna o caminho do arquivo resultante,
    usando ffmpeg binário local na pasta bin/ffmpeg.
    """
    # Defina o binário do ffmpeg
    ffmpeg_bin = "bin/ffmpeg"

    # Pega metadados primeiro
    info = get_video_info(video_url)
    raw_title = info.get("title") or "video_sem_titulo"

    # Sanitiza
    safe_title = sanitize_title(raw_title)

    # Timestamp para não repetir nome
    now_str = datetime.now().strftime("%Y%m%d_%H%M")
    final_name = f"{safe_title}_{now_str}"

    # Garante a pasta videos/
    os.makedirs("videos", exist_ok=True)
    output_path = f"videos/{final_name}.%(ext)s"

    ydl_opts = {
        'outtmpl': output_path,
        'ffmpeg_location': ffmpeg_bin
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    # Detecta qual extensão foi salva
    exts = ["mp4","mkv","webm","m4a","mp3"]
    for ext in exts:
        candidate = f"videos/{final_name}.{ext}"
        if os.path.exists(candidate):
            return candidate

    return None
