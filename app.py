import streamlit as st
import os
import pandas as pd
from backend import (
    get_video_info,
    download_video,
    upload_to_dropbox
)

# Ajuste de config (nome da aba e ícone)
st.set_page_config(
    page_title="Meu Downloader de Vídeos",
    page_icon="📺",
    layout="centered"
)

def main():
    # SIDEBAR
    st.sidebar.title("🎬 Ferramenta Pública de Download")
    st.sidebar.markdown("""
    **O que faz?**
    - Baixa vídeos ou áudio (MP3) do YouTube.
    - Faz upload para o Dropbox em `/streamlit-videos`.
    - Gera um **link** de download para seu dispositivo.
    
    **Instruções**:
    1. Cole a URL do YouTube.
    2. Clique em **Carregar Pré-Visualização** para ver capa e dados.
    3. Escolha **Vídeo** ou **Áudio**.
    4. Clique em **Baixar & Enviar**.
    """)

    st.title("Ferramenta de Download (via Dropbox) 🎉")

    video_url = st.text_input("Cole aqui o link do YouTube:", "")

    # Session state
    if "video_info" not in st.session_state:
        st.session_state.video_info = None
    if "video_url" not in st.session_state:
        st.session_state.video_url = ""

    # Botão para pré-visualizar
    if st.button("🔍 Carregar Pré-Visualização"):
        user_input_url = video_url.strip()
        if user_input_url:
            try:
                info = get_video_info(user_input_url)
                # Se der erro 403 ou outro, cairá no except
                st.session_state.video_info = info
                st.session_state.video_url = user_input_url
                st.success("Pré-visualização carregada!")
            except ValueError as ve:
                if "403" in str(ve):
                    st.error("Erro 403: Este vídeo está bloqueado ou requer login. Tente outro.")
                else:
                    st.error(f"Erro ao carregar dados do vídeo: {ve}")
            except Exception as e:
                st.error(f"Erro ao carregar dados do vídeo: {e}")
        else:
            st.warning("Por favor, insira um link válido.")

    # Exibir info se já carregou
    if st.session_state.video_info:
        info = st.session_state.video_info

        # Exibir thumbnail
        thumbnail = info.get("thumbnail")
        if thumbnail:
            st.image(thumbnail, caption="Capa do Vídeo", use_container_width=True)

        # Informações (título, canal, data, duração)
        title = info.get("title", "Sem título")
        uploader = info.get("uploader", "Desconhecido")
        upload_date = info.get("upload_date")
        if upload_date and len(upload_date) == 8:
            # Converte YYYYMMDD -> DD/MM/YYYY
            upload_date = f"{upload_date[6:]}/{upload_date[4:6]}/{upload_date[0:4]}"

        duration = info.get("duration", 0)
        if duration:
            mins, secs = divmod(duration, 60)
            hours, mins = divmod(mins, 60)
            dur_str = f"{hours}h {mins}m {secs}s" if hours else f"{mins}m {secs}s"
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

        # Botões de tipo de download
        download_type = st.radio(
            "Escolha o tipo de download:",
            ["Vídeo (MP4)", "Áudio (MP3)"]
        )

        if st.button("⬇️ Baixar & Enviar para Dropbox"):
            real_url = st.session_state.video_url.strip()
            if not real_url:
                st.error("URL vazia. Recarregue a pré-visualização.")
                return

            st.info("Baixando...")
            try:
                if download_type == "Áudio (MP3)":
                    downloaded_file = download_video(real_url, download_type="audio")
                else:
                    downloaded_file = download_video(real_url, download_type="video")

                if not downloaded_file or not os.path.exists(downloaded_file):
                    st.error("Não foi possível encontrar o arquivo baixado.")
                    return

                st.info("Enviando ao Dropbox...")
                link = upload_to_dropbox(downloaded_file)
                st.success("Upload concluído! ✅")
                st.markdown(f"[**Clique para download**]({link})")

            except ValueError as ve:
                if "403" in str(ve):
                    st.error("Erro 403 ao baixar: vídeo bloqueado ou requer login.")
                else:
                    st.error(f"Erro ao baixar: {ve}")
            except Exception as e:
                st.error(f"Erro ao baixar ou enviar: {e}")
            finally:
                if downloaded_file and os.path.exists(downloaded_file):
                    os.remove(downloaded_file)

if __name__ == "__main__":
    main()
