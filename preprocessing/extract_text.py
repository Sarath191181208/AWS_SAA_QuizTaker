from cv2 import imread
import pytesseract
from pathlib import Path
from tqdm import tqdm

pytesseract.pytesseract.tesseract_cmd = Path("./tesseract/tesseract.exe").resolve()

def extract_text_from_images(folder_name):
    img_folder = Path(f"./images/{folder_name}")
    img_paths = list(img_folder.glob("*.jpg"))

    for img_path in tqdm(img_paths, desc="Extracting text"):
        img = imread(str(img_path.resolve()))
        text = pytesseract.image_to_string(img)

        # save these texts to a file in the questions folder
        # create a file path
        text_folder = Path("./questions") / folder_name
        # create the folder if it doesn't exist
        text_folder.mkdir(parents=True, exist_ok=True)

        # # write the text to the file
        (text_folder / f"{img_path.stem}.txt").write_text(text)
