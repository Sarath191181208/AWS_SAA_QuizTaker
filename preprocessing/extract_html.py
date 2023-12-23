from pathlib import Path 
import json 
from bs4 import BeautifulSoup


def find_class(text: BeautifulSoup, class_name: str):
    tags = ["div", "p", "span", "ul", "li"]
    for tag in tags: 
        found_text = text.find_all(tag, {"class": class_name})
        if found_text:
            return found_text
    return []

def get_question_number_and_topic(card_header_text: str) -> tuple[str, str]:
    split_text = card_header_text.split("\n")
    # remove empty strings
    split_text = [x for x in split_text if x.strip() != ""]
    # get the question number
    question_number = split_text[0].strip()
    question_topic = split_text[1].strip()
    return question_number, question_topic

def extract_questions_as_json(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "lxml")
# the class to select are card exam-question-card
    questions = soup.find_all("div", {"class": "card exam-question-card"})

# question txt is in this class card-text
# options are in this question-choices-container class
# answer is in vote-bar
    parsed_questions_json = [] 
    for index, question in enumerate(questions):
        try: 
            txt = find_class(question, "card-header")
            inner_text = txt[0].text
            question_number, question_topic = get_question_number_and_topic(inner_text)
            question_text = find_class(question, "card-text")[0].text.strip()
            options_container = find_class(question, "question-choices-container")[0]
            options_lst = find_class(options_container, "multi-choice-item")
            answers = []
            options = []
            for idx, opt in enumerate(options_lst): 
                bs = BeautifulSoup(str(opt), "lxml")
                is_answer = find_class(bs, "correct-hidden")
                if is_answer:
                    answers.append(idx)
                # remove all the span tags 
                for _ in bs.find_all("span"):
                    opt.span.decompose()
                options.append(opt.text.strip())

            # explination class is question-answer
            explination = find_class(question, "question-answer")[0].text.strip()

            parsed_questions_json.append({
                "question": question_number + "\n\n" + question_text,
                "answers": answers,
                "options": options, 
                "explination": explination.replace("\n", " "),
                "topic": question_topic
            })
        except Exception as e:
            print(index)
            continue

    return parsed_questions_json

def main():
    folder = Path(__file__).parent.parent / "htmls"
    json_folder = Path(__file__).parent.parent / "json" / "saa-c02"
    # html_files = list(folder.glob("*.html"))
    # the file names are 13.html, 25.hml, 27.html 
    html_files = [folder / f"{i}.html" for i in [13, 25, 27]]
    failed_files = []
    for file in html_files:
        print(file)
        with open(file, "r", encoding="utf8") as f:
            html = f.read()

        parsed_questions_json = extract_questions_as_json(html)

        # save the json to a file in json/saa-c02/num.json 
        json_folder.mkdir(parents=True, exist_ok=True)
        json_file = json_folder / f"{file.stem}.json"
        with open(json_file, "w", encoding="utf8") as f:
            json.dump(parsed_questions_json, f, indent=4)

    print(f"Failed files: {failed_files}")


if __name__ == "__main__":
    main()

