import streamlit as st
import os
import pandas as pd
from backend import (
    get_video_info,
    download_video,
    upload_to_dropbox
)

def main():
    st.sidebar.title("🎬 Ferramenta Pública de Download")
    st.sidebar.markdown("""
    **O que faz?**
    - Baixa vídeos do YouTube e faz upload para o Dropbox.
    - Gera um **link** para você baixar o arquivo no seu dispositivo.
    
    **Instruções rápidas**:
    1. Cole a URL do vídeo do YouTube.
    2. Clique em **Carregar Pré-Visualização**.
    3. Confira a capa e as informações do vídeo.
    4. Escolha se quer baixar **Vídeo** ou **Áudio (MP3)**.
    5. Clique em **Baixar & Enviar** para receber um link de download.
    """)

    st.title("Ferramenta Pública de Download (via Dropbox) 🎉")

    video_url = st.text_input("Cole aqui o link do YouTube:", "")

    # Guardar metadados na sessão
    if "video_info" not in st.session_state:
        st.session_state.video_info = None

    if st.button("🔍 Carregar Pré-Visualização"):
        if video_url.strip():
            try:
                info = get_video_info(video_url.strip())
                st.session_state.video_info = info
                st.success("Pré-visualização carregada!")
            except Exception as e:
                st.error(f"Erro ao carregar metadados do vídeo: {e}")
        else:
            st.warning("Por favor, insira um link válido.")

    if st.session_state.video_info:
        info = st.session_state.video_info

        # Mostrar thumbnail
        thumbnail = info.get("thumbnail")
        if thumbnail:
            st.image(thumbnail, caption="Capa do Vídeo", use_container_width=True)

        # Montar dados do vídeo
        title = info.get("title", "Sem título")
        uploader = info.get("uploader", "Desconhecido")
        upload_date = info.get("upload_date")
        if upload_date and len(upload_date) == 8:
            upload_date = f"{upload_date[6:]}/{upload_date[4:6]}/{upload_date[0:4]}"

        duration = info.get("duration", 0)
        if duration:
            mins, secs = divmod(duration, 60)
            hours, mins = divmod(mins, 60)
            if hours > 0:
                dur_str = f"{hours}h {mins}m {secs}s"
            else:
                dur_str = f"{mins}m {secs}s"
        else:
            dur_str = "Desconhecida"

        table_data = [
            {"Informação": "Título", "Valor": title},
            {"Informação": "Canal", "Valor": uploader},
            {"Informação": "Data de Postagem", "Valor": upload_date if upload_date else "Desconhecida"},
            {"Informação": "Duração", "Valor": dur_str},
        ]
        df = pd.DataFrame(table_data).set_index("Informação")
        st.table(df)

        # Seletor para escolher vídeo ou áudio
        download_type = st.radio("Escolha o tipo de download:", ["Vídeo (MP4)", "Áudio (MP3)"])

        if st.button("⬇️ Baixar & Enviar para Dropbox"):
            st.info("Baixando...")
            try:
                if download_type == "Áudio (MP3)":
                    downloaded_file = download_video(video_url.strip(), download_type="audio")
                else:
                    downloaded_file = download_video(video_url.strip(), download_type="video")

            except Exception as e:
                st.error(f"Erro ao baixar: {e}")
                return

            if not downloaded_file or not os.path.exists(downloaded_file):
                st.error("Não foi possível encontrar o arquivo baixado.")
                return

            st.info("Enviando ao Dropbox...")
            try:
                link = upload_to_dropbox(downloaded_file)
                st.success("Upload concluído! ✅")
                # Forçar download no Dropbox trocando ?dl=0 -> ?dl=1
                link = link.replace("?dl=0", "?dl=1")
                st.markdown(f"[**Link para download**]({link})")
            except Exception as e:
                st.error(f"Erro ao enviar: {e}")
            finally:
                if os.path.exists(downloaded_file):
                    os.remove(downloaded_file)

if __name__ == "__main__":
    main()
