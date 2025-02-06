import streamlit as st
import os
from backend import (
    get_video_info,
    download_video,
    upload_to_dropbox
)

def main():
    # SIDEBAR COM EXPLICAÇÃO
    st.sidebar.title("🎬 Ferramenta Pública de Download")
    st.sidebar.markdown("""
    **O que faz?**
    - Baixa vídeos do YouTube e faz upload para o Dropbox.
    - Gera um **link** para você baixar o arquivo no seu dispositivo.
    
    **Instruções rápidas**:
    1. Cole a URL do vídeo do YouTube.
    2. Clique em **Carregar Pré-Visualização**.
    3. Confira a capa e as informações do vídeo.
    4. Clique em **Baixar & Enviar** para receber um link de download.
    """)

    st.title("Ferramenta Pública de Download de Vídeos (via Dropbox) 🎉")

    # Campo para o usuário colar o link
    video_url = st.text_input("Cole aqui o link do vídeo do YouTube:", "")

    # Sessão de estado para armazenar as informações
    if "video_info" not in st.session_state:
        st.session_state.video_info = None

    # Botão para pré-visualizar
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

    # Se já temos info do vídeo na sessão, mostramos na tela
    if st.session_state.video_info:
        info = st.session_state.video_info

        # Exibe thumbnail (se existir)
        thumbnail = info.get("thumbnail")
        if thumbnail:
            st.image(thumbnail, caption="Capa do Vídeo", use_container_width=True)

        # Extrai informações
        title = info.get("title", "Sem título")
        uploader = info.get("uploader", "Desconhecido")
        upload_date = info.get("upload_date")  # Formato YYYYMMDD
        if upload_date and len(upload_date) == 8:
            # Converter para algo mais legível (DD/MM/YYYY)
            upload_date = f"{upload_date[6:]}/{upload_date[4:6]}/{upload_date[0:4]}"

        duration = info.get("duration", 0)  # em segundos
        if duration:
            mins, secs = divmod(duration, 60)
            hours, mins = divmod(mins, 60)
            if hours > 0:
                dur_str = f"{hours}h {mins}m {secs}s"
            else:
                dur_str = f"{mins}m {secs}s"
        else:
            dur_str = "Desconhecida"

        # Monta dados para a tabela (cada dict vira uma linha)
        table_data = [
            {"Informação": "Título", "Valor": title},
            {"Informação": "Canal", "Valor": uploader},
            {"Informação": "Data de Postagem", "Valor": upload_date if upload_date else "Desconhecida"},
            {"Informação": "Duração", "Valor": dur_str},
        ]
        
        st.table(table_data)

        # Botão de BAIXAR, somente aparece após ter pré-visualização
        if st.button("⬇️ Baixar & Enviar para Dropbox"):
            st.info("Baixando o vídeo...")
            try:
                downloaded_file = download_video(video_url.strip())
            except Exception as e:
                st.error(f"Erro ao baixar o vídeo: {e}")
                return

            if not downloaded_file or not os.path.exists(downloaded_file):
                st.error("Não foi possível encontrar o arquivo baixado.")
                return

            st.info("Enviando ao Dropbox...")
            try:
                link = upload_to_dropbox(downloaded_file)
                st.success("Upload concluído! ✅")
                # Se quiser forçar o download, troque "?dl=0" por "?dl=1"
                link = link.replace("?dl=0", "?dl=1")
                st.markdown(f"**Link de download**: [Clique aqui]({link})")
            except Exception as e:
                st.error(f"Erro ao enviar para o Dropbox: {e}")
            finally:
                # Remove o arquivo local para não lotar o armazenamento
                if os.path.exists(downloaded_file):
                    os.remove(downloaded_file)

if __name__ == "__main__":
    main()
