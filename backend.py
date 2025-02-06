import os
import re
import dropbox
import yt_dlp
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def sanitize_title(title):
    """
    Remove caracteres que podem causar problemas em nomes de arquivo,
    substitui espaços/hífens repetidos por underscore.
    """
    title = re.sub(r'[^\w\s-]', '', title, flags=re.UNICODE)
    title = re.sub(r'[-\s]+', '_', title.strip())
    return title

def get_video_info(video_url):
    """
    Retorna os metadados do vídeo (título, thumbnail, etc.) sem baixar o conteúdo.
    Se ocorrer 403 (Forbidden), levantamos ValueError para que o app trate.
    """
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(video_url, download=False)
        return info
    except Exception as e:
        # Se a exceção contiver "403", interpretamos como bloqueio (Forbidden).
        if "403" in str(e):
            raise ValueError("403 - Acesso negado ou vídeo bloqueado.")
        # Se for outro erro, relançamos a exceção
        raise e

def download_video(video_url, download_type="video"):
    """
    Baixa o vídeo ou áudio (MP3) usando yt_dlp e retorna o caminho do arquivo final.
    """
    ffmpeg_bin = "bin/ffmpeg"  # binário ffmpeg incluso no repositório

    # Primeiro, obtemos as infos para extrair o título
    # (Se o vídeo for 403, deve dar erro aqui também, mas normalmente
    #  já será detectado no get_video_info anterior)
    info = get_video_info(video_url)

    raw_title = info.get("title", "video_sem_titulo")
    safe_title = sanitize_title(raw_title)

    # Pasta local para armazenar
    os.makedirs("videos", exist_ok=True)
    now_str = datetime.now().strftime("%Y%m%d_%H%M")
    final_name = f"{safe_title}_{now_str}"

    # Define opções do yt_dlp de acordo com o tipo (vídeo ou áudio)
    if download_type == "audio":
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
        ydl_opts = {
            'outtmpl': f'videos/{final_name}.%(ext)s',
            'ffmpeg_location': ffmpeg_bin,
        }
        expected_extensions = ["mp4", "mkv", "webm"]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    # Descobre o arquivo final
    for ext in expected_extensions:
        path_candidate = f"videos/{final_name}.{ext}"
        if os.path.exists(path_candidate):
            return path_candidate

    return None

def upload_to_dropbox(file_path):
    """
    Envia o arquivo para /streamlit-videos no Dropbox e retorna link de download (?dl=1).
    """
    dropbox_token = os.getenv("DROPBOX_ACCESS_TOKEN")
    if not dropbox_token:
        raise ValueError("DROPBOX_ACCESS_TOKEN não definido (verifique .env ou Secrets).")

    dbx = dropbox.Dropbox(dropbox_token)
    folder_name = "/streamlit-videos"

    # Garante a existência da pasta
    try:
        dbx.files_create_folder_v2(folder_name)
    except dropbox.exceptions.ApiError as e:
        if "folder_conflict" not in str(e):
            raise e

    dropbox_path = f"{folder_name}/{os.path.basename(file_path)}"
    with open(file_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))

    link_info = dbx.sharing_create_shared_link_with_settings(dropbox_path)
    # Força download trocando ?dl=0 -> ?dl=1
    final_link = link_info.url.replace("?dl=0", "?dl=1")
    return final_link
