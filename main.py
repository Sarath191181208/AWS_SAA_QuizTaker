from yt_download import download_video_and_description
from extract_images import extract_images_from_video, extract_time_stamps
from extract_text import extract_text_from_images

file_name = "q5"
# yt_video_url = "https://www.youtube.com/watch?v=nL-OQ76_U4Q"

# # download_video_and_description(yt_video_url, file_name)
# time_stamps = extract_time_stamps(file_name)
time_stamps = [
    "24:49"
]
out_folder = f"{file_name}_invalid_3"
# print(time_stamps)
extract_images_from_video(time_stamps, file_name, out_folder)
extract_text_from_images(out_folder)
