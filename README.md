# ⬇️ YouTube to Dropbox Downloader ☁️

Baixe vídeos do YouTube e envie-os direto para o seu Dropbox! 🚀 Aplicação web simples, criada com Streamlit, Python, e a API do Dropbox.

## ✨ Funcionalidades

*   **⬇️ Download:** Cole o link do YouTube e baixe o vídeo.
*   **☁️ Upload:** Envio automático para a sua pasta no Dropbox.
*   **📱 Interface:** Design intuitivo com Streamlit.
*   **🌐 Online:** Hospedado no Streamlit Cloud.

## 🛠️ Tecnologias

*   **🐍 Python:** Backend da aplicação.
*   **Streamlit:** Framework para a interface web.
*   **yt-dlp:** Biblioteca para download de vídeos.
*   **Dropbox API:** Integração com o Dropbox.
*   **Streamlit Cloud:** Hospedagem da aplicação.

## 🕹️ Como Usar

1.  Acesse a aplicação (link fornecido pelo Streamlit Cloud).
2.  Insira o link do vídeo do YouTube.
3.  Clique em "Baixar e Enviar para o Dropbox".
4.  Aguarde o processo.
5.  Vídeo disponível na pasta `/videos/` no seu Dropbox.

## ⚙️ Configuração (Devs)

1.  Clone o repo.
2.  `pip install -r requirements.txt`.
3.  Crie um App no [Dropbox Developer Console](https://www.dropbox.com/developers/apps).
4.  Defina `DROPBOX_TOKEN` como variável de ambiente.
5.  `streamlit run app.py`.

## ⚠️ Notas

*   🔒 **`DROPBOX_TOKEN`:** Guarde sua chave como variável de ambiente.
*   ☁️ **Streamlit Cloud:** Atenção ao tempo limite de execução.
*   ⚖️ **Responsabilidade:** Use a ferramenta de acordo com os termos do YouTube e leis de direitos autorais.

## 📜 Licença

[MIT License](LICENSE)