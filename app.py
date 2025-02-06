import streamlit as st
import backend  # Importa o script backend.py
import os

st.title("Baixar Vídeos do YouTube e Enviar para o Dropbox")

video_url = st.text_input("Digite o link do vídeo do YouTube:")

if st.button("Baixar e Enviar para o Dropbox"):
    if video_url:
        st.info("Baixando o vídeo...")
        local_file = backend.download_video(video_url, "meus_videos") # Salva na pasta "meus_videos" localmente

        if local_file:
            st.success("Vídeo baixado com sucesso!")
            dropbox_path = f"/videos/{os.path.basename(local_file)}"
            st.info("Enviando para o Dropbox...")
            if backend.upload_to_dropbox(local_file, dropbox_path):
                st.success("Vídeo enviado para o Dropbox com sucesso!")
                backend.delete_local_file(local_file)
                st.info("Arquivo local deletado.")
            else:
                st.error("Erro ao enviar para o Dropbox.")
        else:
            st.error("Erro ao baixar o vídeo. Verifique o link.")
    else:
        st.warning("Por favor, digite o link do vídeo.")