import streamlit as st
import os

# Importa as funções do backend
from backend import download_video, upload_to_dropbox

def main():
    st.title("YouTube Downloader + Upload para Dropbox (Separado em backend.py)")

    video_url = st.text_input("Cole aqui o link do vídeo do YouTube")

    if st.button("Baixar e Enviar para Dropbox"):
        if video_url:
            st.info("Baixando o vídeo...")
            downloaded_file = download_video(video_url)

            if not downloaded_file:
                st.error("Não foi possível baixar o vídeo ou encontrar o arquivo.")
                return

            st.info("Enviando o vídeo ao Dropbox...")
            try:
                link = upload_to_dropbox(downloaded_file)
                st.success("Upload concluído!")
                st.write(f"[Link do vídeo no Dropbox]({link})")
            except Exception as e:
                st.error(f"Ocorreu um erro ao enviar para o Dropbox: {e}")
            finally:
                # Limpa o arquivo local para não lotar armazenamento
                if downloaded_file and os.path.exists(downloaded_file):
                    os.remove(downloaded_file)
        else:
            st.warning("Por favor, insira uma URL de vídeo válida.")

if __name__ == "__main__":
    main()
