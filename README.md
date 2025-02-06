# YouTube to Dropbox Downloader

Este projeto é uma aplicação web simples que permite aos usuários baixar vídeos do YouTube e enviá-los diretamente para suas contas do Dropbox.  A aplicação utiliza [Streamlit](https://streamlit.io/) para a interface do usuário (frontend), [Python](https://www.python.org/) no backend para o processo de download e upload, e o [Dropbox API](https://www.dropbox.com/developers/documentation) para o armazenamento dos vídeos.

## Funcionalidades

*   **Download de Vídeos do YouTube:** Insira o link de um vídeo do YouTube, e o backend, utilizando a biblioteca `yt-dlp`, fará o download do vídeo.
*   **Upload para o Dropbox:** Após o download, o vídeo é automaticamente enviado para uma pasta especificada na sua conta do Dropbox.
*   **Interface Simples e Intuitiva:** Graças ao Streamlit, a aplicação oferece uma interface fácil de usar para qualquer usuário.
*   **Hospedagem no Streamlit Cloud:** A aplicação está hospedada no [Streamlit Cloud](https://streamlit.io/cloud), facilitando o acesso e o compartilhamento.

## Tecnologias Utilizadas

*   **Streamlit:** Framework Python para criar interfaces web interativas.
*   **Python:** Linguagem de programação utilizada para o backend.
*   **yt-dlp:** Biblioteca Python para baixar vídeos de plataformas como o YouTube.
*   **Dropbox API:** API para interagir com o serviço de armazenamento em nuvem Dropbox.
*   **Streamlit Cloud:** Plataforma para hospedar e compartilhar aplicações Streamlit.

## Como Usar

1.  Acesse a aplicação através do link fornecido pelo Streamlit Cloud.
2.  Insira o link do vídeo do YouTube no campo de texto.
3.  Clique no botão "Baixar e Enviar para o Dropbox".
4.  Aguarde o processo de download e upload ser concluído. Mensagens informativas serão exibidas durante o processo.
5.  O vídeo estará disponível na pasta `/videos/` (ou na pasta configurada) em sua conta do Dropbox.

## Configuração (Para Desenvolvedores)

1.  Clone este repositório para sua máquina local.
2.  Instale as dependências: `pip install -r requirements.txt`.
3.  Crie um app no [Dropbox Developer Console](https://www.dropbox.com/developers/apps) e obtenha um token de acesso.
4.  Defina o token de acesso como uma variável de ambiente chamada `DROPBOX_TOKEN`.
5.  Execute a aplicação localmente: `streamlit run app.py`.

## Notas Importantes

*   **Variável de Ambiente `DROPBOX_TOKEN`:** Nunca coloque seu token do Dropbox diretamente no código. Utilize variáveis de ambiente para armazenar informações sensíveis.
*   **Streamlit Cloud:** A aplicação está configurada para ser hospedada no Streamlit Cloud, que oferece uma maneira fácil de fazer deploy de aplicações Streamlit.
*   **Limitações do Streamlit Cloud:** O Streamlit Cloud tem limitações de tempo de execução.  Se o download ou upload demorar muito, o Streamlit Cloud pode encerrar o processo.
*   **Tratamento de Erros:** A aplicação inclui tratamento básico de erros, mas pode ser aprimorado para fornecer feedback mais detalhado aos usuários.
*   **Responsabilidade:** O usuário é responsável por garantir que o download e a distribuição de vídeos do YouTube estejam em conformidade com os termos de serviço do YouTube e as leis de direitos autorais aplicáveis.

