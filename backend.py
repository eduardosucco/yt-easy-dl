import os
import tarfile
import subprocess
import stat

import yt_dlp
import dropbox
from dotenv import load_dotenv

# Carrega variáveis de ambiente locais (.env) -- em produção (Streamlit Cloud),
# você usaria Secrets, mas se quiser usar local, deixe aqui.
load_dotenv()

def setup_ffmpeg():
    """
    Faz download de um build estático do ffmpeg (para Linux x86_64) e coloca em /tmp/ffmpeg.
    Retorna o caminho completo do binário baixado.
    Caso já exista, não baixa novamente.
    """
    ffmpeg_bin = "/tmp/ffmpeg"

    # Se o arquivo já existe, não faz download de novo
    if not os.path.isfile(ffmpeg_bin):
        print("Baixando ffmpeg estático pela primeira vez...")

        # URL para baixar o ffmpeg estático (Linux x86_64).
        # Você pode alterar para outra versão/arquitetura se necessário.
        url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        out_tgz = "/tmp/ffmpeg.tar.xz"

        # Baixa via subprocess + wget
        subprocess.run(["wget", url, "-O", out_tgz], check=True)

        # Extrai o .tar.xz
        with tarfile.open(out_tgz, "r:xz") as tar:
            tar.extractall(path="/tmp")

        # Localiza a pasta extraída, por exemplo: /tmp/ffmpeg-5.1.2-amd64-static
        folder_name = None
        for fname in os.listdir("/tmp"):
            full_path = os.path.join("/tmp", fname)
            if fname.startswith("ffmpeg") and os.path.isdir(full_path):
                folder_name = fname
                break

        if not folder_name:
            raise RuntimeError("Não foi possível localizar a pasta de ffmpeg após extração.")

        # Move/renomeia o binário principal "ffmpeg" para /tmp/ffmpeg
        extracted_ffmpeg = os.path.join("/tmp", folder_name, "ffmpeg")
        os.rename(extracted_ffmpeg, ffmpeg_bin)

        # Dá permissão de execução
        st = os.stat(ffmpeg_bin)
        os.chmod(ffmpeg_bin, st.st_mode | stat.S_IEXEC)

        print("ffmpeg baixado e pronto em /tmp/ffmpeg")

    return ffmpeg_bin

def download_video(video_url, filename="video_downloaded"):
    """
    Faz o download do vídeo usando yt_dlp e retorna o nome completo do arquivo baixado.
    """
    ffmpeg_bin = setup_ffmpeg()  # Garante que o ffmpeg está disponível

    ydl_opts = {
        # Passa o caminho do ffmpeg baixado
        'ffmpeg_location': ffmpeg_bin,
        'outtmpl': f'{filename}.%(ext)s'  # Define o nome base do arquivo
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    
    # Descobre qual extensão foi gerada
    possible_extensions = ["mp4", "mkv", "webm"]
    for ext in possible_extensions:
        full_name = f"{filename}.{ext}"
        if os.path.exists(full_name):
            return full_name
    
    return None

def upload_to_dropbox(file_path):
    """
    Faz upload do arquivo para o Dropbox e retorna um link compartilhável.
    O token é lido de variável de ambiente "DROPBOX_ACCESS_TOKEN".
    """
    dropbox_token = os.getenv("DROPBOX_ACCESS_TOKEN", None)
    if not dropbox_token:
        raise ValueError("Token do Dropbox não encontrado. Verifique seu .env ou Secrets.")

    dbx = dropbox.Dropbox(dropbox_token)

    # Nome do arquivo/pasta no Dropbox
    dropbox_path = f"/{os.path.basename(file_path)}"

    with open(file_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))

    # Cria link compartilhável
    shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
    return shared_link_metadata.url
