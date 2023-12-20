import sys
from pathlib import Path
import pytube
from pytube.cli import on_progress

def download_video_and_description(yt_video_url: str, file_name: str):
    Path("./videos").mkdir(parents=True, exist_ok=True)
    video_path = Path("./videos") / f"{file_name}.mp4"
    if video_path.exists():
        print("Video already exists")
        sys.exit(0)

    youtube = pytube.YouTube(yt_video_url, on_progress_callback=on_progress)
    video_stream = youtube.streams.filter(res="1080p").first()

    if video_stream is None:
        print("No 720p video stream available")
        sys.exit(0)

    video_stream.download(filename=str(video_path.resolve()))

    # Save the description
    description_path = Path("./videos") / f"{file_name}.txt"
    description_path.write_text(youtube.description)
