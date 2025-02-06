import streamlit as st
import os
import pandas as pd
from backend import (
    get_video_info,
    download_video,
    upload_to_dropbox
)

# Configuração da página (nome da aba e favicon):
st.set_page_config(
    page_title="Ferramenta de Download",
    page_icon="📺",  # Pode ser um emoji ou URL de imagem
    layout="centered"
)

def main():
    # --- SIDEBAR ---
    st.sidebar.title("🎬 Ferramenta Pública de Download")
    st.sidebar.markdown("""
    **O que faz?**
    - Baixa vídeos ou áudio (MP3) do YouTube
    - Faz upload para Dropbox em `/streamlit-videos`
    - Gera link de download

    **Instruções**:
    1. Cole a URL do YouTube
    2. Clique **Carregar Pré-Visualização** (exibe capa e dados, se permitido)
    3. Escolha **Vídeo** ou **Áudio**
    4. Clique **Baixar & Enviar**
    """)

    st.title("Ferramenta de Download (via Dropbox) 🎉")

    video_url = st.text_input("Cole aqui o link do YouTube:")

    # Session state para armazenar metadados do vídeo e a URL
    if "video_info" not in st.session_state:
        st.session_state.video_info = None
    if "video_url" not in st.session_state:
        st.session_state.video_url = ""

    # Botão de pré-visualizar
    if st.button("🔍 Carregar Pré-Visualização"):
        url_lido = video_url.strip()
        if not url_lido:
            st.warning("Por favor, insira um link válido.")
        else:
            try:
                info = get_video_info(url_lido)
                # Se não houve erro, armazenamos no session state
                st.session_state.video_info = info
                st.session_state.video_url = url_lido
                st.success("Pré-visualização carregada!")
            except ValueError as ve:
                # Se for 403 ou outro
                if "403" in str(ve):
                    st.error("Erro 403: Acesso negado ou vídeo bloqueado.")
                else:
                    st.error(f"Erro ao carregar dados do vídeo: {ve}")
            except Exception as e:
                st.error(f"Erro ao carregar dados do vídeo: {e}")

    # Exibir informações apenas se `video_info` foi carregado
    if st.session_state.video_info:
        info = st.session_state.video_info

        # Exibe thumbnail, se existir
        thumbnail = info.get("thumbnail")
        if thumbnail:
            st.image(thumbnail, caption="Capa do Vídeo", use_container_width=True)

        # Extrai dados: título, canal, data, duração
        title = info.get("title", "Sem título")
        uploader = info.get("uploader", "Desconhecido")

        upload_date = info.get("upload_date")
        if upload_date and len(upload_date) == 8:
            # Formato YYYYMMDD -> DD/MM/YYYY
            upload_date = f"{upload_date[6:]}/{upload_date[4:6]}/{upload_date[0:4]}"
        else:
            upload_date = "Desconhecida"

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

        # Montar dados em tabela (sem índice numérico)
        table_data = [
            {"Informação": "Título", "Valor": title},
            {"Informação": "Canal", "Valor": uploader},
            {"Informação": "Data de Postagem", "Valor": upload_date},
            {"Informação": "Duração", "Valor": dur_str},
        ]
        df = pd.DataFrame(table_data).set_index("Informação")
        st.table(df)

        # Opção de vídeo ou áudio
        download_type = st.radio(
            "Escolha o tipo de download:",
            ["Vídeo (MP4)", "Áudio (MP3)"]
        )

        # Botão de baixar
        if st.button("⬇️ Baixar & Enviar"):
            # Verifica URL da sessão
            real_url = st.session_state.video_url.strip()
            if not real_url:
                st.error("URL vazia. Refaça a pré-visualização.")
                return

            downloaded_file = None  # Para evitar UnboundLocalError
            try:
                st.info("Baixando...")
                if download_type == "Áudio (MP3)":
                    downloaded_file = download_video(real_url, download_type="audio")
                else:
                    downloaded_file = download_video(real_url, download_type="video")

                if not downloaded_file or not os.path.exists(downloaded_file):
                    st.error("Não foi possível localizar o arquivo baixado.")
                    return

                st.info("Enviando ao Dropbox...")
                link = upload_to_dropbox(downloaded_file)
                st.success("Upload concluído!")
                st.markdown(f"[**Link para download**]({link})")

            except ValueError as ve:
                if "403" in str(ve):
                    st.error("Erro 403 ao baixar: Acesso negado / vídeo bloqueado.")
                else:
                    st.error(f"Erro ao baixar: {ve}")
            except Exception as e:
                st.error(f"Erro ao baixar ou enviar: {e}")
            finally:
                # Remove o arquivo local se existir
                if downloaded_file and os.path.exists(downloaded_file):
                    os.remove(downloaded_file)


if __name__ == "__main__":
    main()
