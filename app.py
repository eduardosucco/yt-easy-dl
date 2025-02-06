import streamlit as st
import yt_dlp
import dropbox
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class YouTubeDownloader:
    def __init__(self):
        # Initialize Dropbox client
        self.dbx = dropbox.Dropbox(os.getenv('DROPBOX_TOKEN'))
    
    def download_video(self, video_url):
        """Download video using yt-dlp and upload to Dropbox"""
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': '%(title)s.%(ext)s',  # Output template
                'format': 'best',  # Best available quality
            }
            
            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=True)
                video_title = ydl.prepare_filename(info_dict)
            
            # Upload to Dropbox
            with open(video_title, 'rb') as file:
                self.dbx.files_upload(file.read(), f'/downloads/{os.path.basename(video_title)}')
            
            # Remove local file
            os.remove(video_title)
            
            return True, video_title
        
        except Exception as e:
            return False, str(e)

def main():
    st.title('YouTube Video Downloader')
    
    # Video URL input
    video_url = st.text_input('Enter YouTube Video URL')
    
    # Download button
    if st.button('Download Video'):
        if video_url:
            downloader = YouTubeDownloader()
            success, result = downloader.download_video(video_url)
            
            if success:
                st.success(f'Video downloaded and uploaded to Dropbox: {os.path.basename(result)}')
            else:
                st.error(f'Download failed: {result}')
        else:
            st.warning('Please enter a valid YouTube URL')

if __name__ == '__main__':
    main()