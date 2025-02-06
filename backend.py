import yt_dlp
import dropbox
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis de ambiente do arquivo .env (opcional)

DROPBOX_TOKEN = os.environ.get("DROPBOX_TOKEN")  # Sua chave de acesso do Dropbox

def download_video(video_url, output_path="."):
    """Baixa um vídeo do YouTube e retorna o caminho do arquivo."""
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s-%(id)s.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',  # Melhor qualidade de vídeo e áudio
        'quiet': True, # Suprime a saída verbosa
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(video_url, download=True)
                video_filename = ydl.prepare_filename(info_dict) # Obtem o nome do arquivo baixado
                return video_filename
            except Exception as e:
                print(f"Erro ao extrair informações do vídeo: {e}")
                return None
    except Exception as e:
        print(f"Erro ao inicializar yt-dlp: {e}")
        return None

def upload_to_dropbox(local_path, dropbox_path):
    """Envia um arquivo para o Dropbox."""
    try:
        dbx = dropbox.Dropbox(DROPBOX_TOKEN)
        with open(local_path, "rb") as f:
            dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
        print(f"Arquivo {local_path} enviado para {dropbox_path} no Dropbox.")
        return True
    except Exception as e:
        print(f"Erro ao enviar para o Dropbox: {e}")
        return False

def delete_local_file(local_path):
    """Deleta um arquivo local."""
    try:
        os.remove(local_path)
        print(f"Arquivo {local_path} deletado localmente.")
    except Exception as e:
        print(f"Erro ao deletar o arquivo: {e}")

if __name__ == '__main__':
    # Teste (remova isso quando integrar com o Streamlit)
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Exemplo
    local_file = download_video(video_url, "meus_videos")
    if local_file:
        dropbox_path = f"/videos/{os.path.basename(local_file)}"  # Pasta "videos" no Dropbox
        if upload_to_dropbox(local_file, dropbox_path):
            delete_local_file(local_file) # Limpa o arquivo local após o upload