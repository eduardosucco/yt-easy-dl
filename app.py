import streamlit as st
import os
import pandas as pd
from backend import (
    get_video_info,
    download_video,
    upload_to_dropbox
)

# Defina a configuração da página (deve vir antes de qualquer comando que "desenhe" a página):
st.set_page_config(
    page_title="Meu Downloader de Vídeos",  # Nome que aparecerá na aba do navegador
    page_icon="📺",                       # Pode ser um emoji, ou uma URL de imagem
    layout="centered",                    # 'centered' ou 'wide'
    initial_sidebar_state="expanded"      # se quiser começar com a barra lateral aberta
)

def main():
    # --- SIDEBAR ---
    st.sidebar.title("🎬 Ferramenta Pública de Download")
    st.sidebar.markdown("""
    **O que faz?**
    - Baixa vídeos ou áudio (MP3) do YouTube.
    - Gera um **link** para você baixar o arquivo no seu dispositivo.
    
    **Instruções**:
    1. Cole a URL do vídeo do YouTube.
    2. Clique em **Carregar Pré-Visualização** para ver capa e dados.
    3. Escolha **Vídeo** ou **Áudio**.
    4. Clique em **Baixar & Enviar** para receber o link de download.
    """)

    st.title("Ferramenta de Download (via Dropbox) 🎉")

    video_url = st.text_input("Cole aqui o link do YouTube:", "")

    # Session state para guardar metadados e URL
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
                st.session_state.video_info = info
                st.session_state.video_url = user_input_url
                st.success("Pré-visualização carregada!")
            except Exception as e:
                # Aqui, se for um erro 403 ou algo específico,
                # você pode checar, por ex: if "403" in str(e) ...
                st.error(f"Erro ao carregar metadados do vídeo (talvez bloqueado): {e}")
        else:
            st.warning("Por favor, insira um link válido.")


    # Se já temos info do vídeo
    if st.session_state.video_info:
        info = st.session_state.video_info

        # Exibir thumbnail
        thumbnail = info.get("thumbnail")
        if thumbnail:
            # use_container_width em vez de use_column_width
            st.image(thumbnail, caption="Capa do Vídeo", use_container_width=True)

        # Título, canal, data, duração
        title = info.get("title", "Sem título")
        uploader = info.get("uploader", "Desconhecido")
        upload_date = info.get("upload_date")
        if upload_date and len(upload_date) == 8:
            # Converter para DD/MM/YYYY
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

        # Criar dataframe para exibir como tabela
        table_data = [
            {"Informação": "Título", "Valor": title},
            {"Informação": "Canal", "Valor": uploader},
            {"Informação": "Data de Postagem", "Valor": upload_date if upload_date else "Desconhecida"},
            {"Informação": "Duração", "Valor": dur_str},
        ]
        df = pd.DataFrame(table_data).set_index("Informação")
        st.table(df)

        # Radio para escolher entre vídeo ou áudio
        download_type = st.radio(
            "Escolha o tipo de download:",
            ["Vídeo (MP4)", "Áudio (MP3)"]
        )

        # Botão de baixar
        if st.button("⬇️ Baixar & Enviar para Dropbox"):
            # Verifica se temos URL válida
            real_url = st.session_state.video_url.strip()
            if not real_url:
                st.error("URL vazia. Carregue a pré-visualização novamente.")
                return

            st.info("Baixando...")
            try:
                if download_type == "Áudio (MP3)":
                    downloaded_file = download_video(real_url, download_type="audio")
                else:
                    downloaded_file = download_video(real_url, download_type="video")
            except Exception as e:
                st.error(f"Erro ao baixar: {e}")
                return

            if not downloaded_file or not os.path.exists(downloaded_file):
                st.error("Não foi possível encontrar o arquivo baixado.")
                return

            # Upload
            st.info("Enviando ao Dropbox...")
            try:
                link = upload_to_dropbox(downloaded_file)
                st.success("Upload concluído! ✅")
                # Forçar download
                link = link.replace("?dl=0", "?dl=1")
                st.markdown(f"[**Link para download**]({link})")
            except Exception as e:
                st.error(f"Erro ao enviar para Dropbox: {e}")
            finally:
                # Remove local
                if os.path.exists(downloaded_file):
                    os.remove(downloaded_file)

if __name__ == "__main__":
    main()
