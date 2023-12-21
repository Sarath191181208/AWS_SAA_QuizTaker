"""
Helper script to find missing questions and repeated questions
"""
import json
import re
from collections import Counter
from pathlib import Path

CURRENT_FOLDER = Path(__file__).parent
JSON_FILE = CURRENT_FOLDER.parent/"data.json"
# read the question_answers.json file
with open( JSON_FILE, encoding="utf-8") as f:
    question_answers = json.load(f)


def extract_num_from_dict(questions_and_ans_dict: dict) -> int | None:
    """
    Extracts the number from the question and returns it from Question.question
    if the question starts with Q otherwise returns None
    """
    # get the question
    question = questions_and_ans_dict["question"]
    lines = question.splitlines()
    if len(lines) == 0:
        print("EMPTY:", questions_and_ans_dict)
        return 0
    # get the first line
    first_line = lines[0]

    if not first_line.startswith("Q"):
        print("--" * 20)
        print("NOT STARTS WITH Q:", questions_and_ans_dict)
        print("--" * 20)
        return 0

    # get the number from the first line
    pattern = re.compile(r"\d+")
    if res := pattern.search(first_line):
        return int(res.group())

    return None


def check_repeated_missing_and_low_options():
    numbers: list[int] = list()
    for ques_ans_dict in question_answers:
        num = extract_num_from_dict(ques_ans_dict)
        if num is not None:
            numbers.append(num)
        else:
            print("NONE:", ques_ans_dict)

    # find if the count is greater than 1 for any number
    counter = Counter(numbers)
    repeated = list()
    for number, count in counter.items():
        if count > 1:
            repeated.append(number)

    missing = []
    # find missing numbers
    for i in range(1, 201):
        if i not in numbers:
            missing.append(i)

    low_options = []
    for ques_ans_dict in question_answers:
        options = ques_ans_dict["options"]
        if len(options) < 4:
            num = extract_num_from_dict(ques_ans_dict)
            if num is None :
                continue
            low_options.append(num)

    print("REPEATED:", sorted(repeated))
    print("MISSING:", sorted(missing), "TOTAL:", len(missing))
    print("LOW OPTIONS:", sorted(low_options), "TOTAL:", len(low_options))

def sort_json_on_ques_no(data: list[dict]) -> list[dict]:
    question_numbers = [ extract_num_from_dict(ques_ans_dict) for ques_ans_dict in data ]
    data = [ x for _, x in sorted(zip(question_numbers, data)) ]
    return data

if __name__ == "__main__":
    # check_repeated_missing_and_low_options()
    sorted_data = sort_json_on_ques_no(question_answers)
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, indent=4)
