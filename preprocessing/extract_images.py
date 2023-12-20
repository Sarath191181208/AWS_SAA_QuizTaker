import re
from pathlib import Path
import subprocess
from tqdm import tqdm


def extract_time_stamps(file_name: str) -> list[str]:
    # read the text fro mthe file_name + ".txt" file
    description_path = Path("./videos") / f"{file_name}.txt"

    # read the text from the file
    description_text = description_path.read_text()

    # split the text into lines
    description_lines = description_text.splitlines()

    # find the line with the timestamp use regex to find the timestamp
    # the pattern could be something like this: 00:00:00 or 00:00
    pattern = re.compile(r"(\d{1,2}:)?\d{1,2}:\d{1,2}")
    time_stamps = []
    for line in description_lines:
        if res := pattern.search(line):
            time_stamps.append(res.group())

    return time_stamps


def extract_images_from_video(
    time_stamps: list[str], file_name: str, out_folder_name: str | None = None
) -> None:
    # for each time stamp, extract the image from the video
    vid_file_path = Path("./videos") / f"{file_name}.mp4"

    out_folder_name = out_folder_name or file_name
    # create a folder for the images
    images_folder = Path("./images") / out_folder_name

    # create the folder if it doesn't exist
    images_folder.mkdir(parents=True, exist_ok=True)

    # extract the images

    for i, time_stamp in tqdm(enumerate(time_stamps), desc="Extracting images"):
        # create the output file path
        output_file_path = images_folder / f"{i}.jpg"
        # run the ffmpeg command
        subprocess.run(
            [
                "ffmpeg",
                "-ss",
                time_stamp,
                "-i",
                vid_file_path,
                "-vframes",
                "1",
                "-q:v",
                "2",
                str(output_file_path.resolve()),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
