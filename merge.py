from pathlib import Path
import re
import json
from tqdm import tqdm


# read a file from questions/ q1_1080 / 1.txt
def seperate_question_and_options(file: Path) -> tuple[str, list[str]]:
    text = file.read_text()

    # split the text into lines
    lines = text.splitlines()

    # find the line with the pattern 'A.' to seperate the question and options
    pattern = re.compile(r"^[A-Z]\.")
    question_until = 0
    for i, line in enumerate(lines):
        if pattern.search(line):
            question_until = i
            break

    # join the lines from 0 to question_until to get the question
    question = "\n".join(lines[:question_until])

    # get the options array
    options = []
    temp_str = ""
    for line in lines[question_until:]:
        if line == "":
            continue
        if line.strip().startswith("PRESENTATION TITLE"):
            continue
        if pattern.search(line):
            options.append(temp_str)
            temp_str = ""
        temp_str += line
    options.append(temp_str)
    options = options[1:]

    # remove the prefix from the options
    options = [option[3:] for option in options]

    return question, options


def extract_to_json(files: list[Path]) -> list[dict]:
    question_answers_json = []
    for file in tqdm(files):
        question, options = seperate_question_and_options(file)
        # the answer is unknown just save ""
        question_answers_json.append(
            {"question": question, "options": options, "answers": []}
        )

    return question_answers_json


# read all the file from questions folder including the subfolders
# all_files = list(Path("./questions").rglob("*.txt"))
# read all the files fro questions folder and the subfolder ending with _invalid
all_files = list(Path("./questions").glob("q5_invalid_3/*.txt"))
question_answers_json = extract_to_json(all_files)

with open("question_answers_invalid_3.json", "w") as f:
    json.dump(question_answers_json, f, indent=4)

# read question_answers.json and question_answers_invalid.json
# and merge them into one file
# with open("question_answers_merged.json", "r") as f:
#     question_answers = json.load(f)

# with open("question_answers_invalid_2.json", "r") as f:
#     question_answers_invalid = json.load(f)

# question_answers.extend(question_answers_invalid)

# with open("question_answers_merged_2.json", "w") as f:
#     json.dump(question_answers, f, indent=4)
