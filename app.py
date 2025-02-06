import streamlit as st
import os
from backend import download_video, upload_to_dropbox

def main():
    st.title("Ferramenta Pública de Download de Vídeos (via Dropbox)")

    video_url = st.text_input("Cole aqui o link do vídeo do YouTube")

    if st.button("Baixar e Gerar Link"):
        if video_url:
            st.info("Baixando o vídeo...")
            try:
                downloaded_file = download_video(video_url)
            except Exception as e:
                st.error(f"Erro ao baixar o vídeo: {e}")
                return

            if not downloaded_file:
                st.error("Não foi possível encontrar o arquivo baixado.")
                return

            st.info("Fazendo upload para Dropbox e gerando link...")
            try:
                link = upload_to_dropbox(downloaded_file)
                st.success("Upload concluído!")
                st.write("Clique no link abaixo para baixar o vídeo:")
                st.write(link)
            except Exception as e:
                st.error(f"Erro ao enviar para o Dropbox: {e}")
            finally:
                # Remove o arquivo local
                if os.path.exists(downloaded_file):
                    os.remove(downloaded_file)
        else:
            st.warning("Por favor, insira um link válido.")

if __name__ == "__main__":
    main()
