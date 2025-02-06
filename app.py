import streamlit as st
import yt_dlp
import dropbox
import os

# Para ler o .env localmente
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

def download_video(video_url, filename="video_downloaded"):
    """Faz o download do vídeo usando yt_dlp.Retorna o nome completo do arquivo baixado (com extensão)."""
    ydl_opts = {
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
    """Faz upload do arquivo para o Dropbox e retorna um link compartilhável."""
    # Carrega o token do Dropbox a partir das variáveis de ambiente (ou .env)
    dropbox_token = os.getenv("DROPBOX_ACCESS_TOKEN", None)
    if not dropbox_token:
        raise ValueError("Token do Dropbox não encontrado. Verifique seu .env ou variáveis de ambiente.")

    dbx = dropbox.Dropbox(dropbox_token)

    # Caminho no Dropbox (raiz do seu app ou pasta específica).
    dropbox_path = f"/{os.path.basename(file_path)}"

    # Faz upload
    with open(file_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))

    # Cria link compartilhável
    shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
    return shared_link_metadata.url

def main():
    st.title("YouTube Downloader com Upload para Dropbox")

    # Campo para inserir a URL do vídeo
    video_url = st.text_input("Cole aqui o link do vídeo do YouTube")

    if st.button("Baixar e Enviar para Dropbox"):
        if video_url:
            st.info("Baixando o vídeo...")
            downloaded_file = download_video(video_url)

            if downloaded_file is None:
                st.error("Não foi possível baixar o vídeo ou encontrar o arquivo.")
                return

            st.info("Enviando o vídeo ao Dropbox...")
            try:
                link = upload_to_dropbox(downloaded_file)
                st.success("Upload concluído!")
                st.write(f"Link do vídeo no Dropbox: {link}")
            except Exception as e:
                st.error(f"Ocorreu um erro ao enviar para o Dropbox: {e}")
            finally:
                # Limpa o arquivo local para não lotar armazenamento
                if os.path.exists(downloaded_file):
                    os.remove(downloaded_file)
        else:
            st.warning("Por favor, insira uma URL de vídeo válida.")

if __name__ == "__main__":
    main()
