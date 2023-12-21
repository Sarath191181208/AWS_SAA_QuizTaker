"""
This module contains the functions related to the quiz
"""

import json
import random
from dataclasses import asdict, dataclass
from copy import deepcopy


@dataclass
class Question:
    """
    Question dataclass
    """

    index: int
    question: str
    answers: list[int]
    options: list[str]
    total_times_question_attempted: int
    correct_times_question_attempted: int
    current_probability: float


QUESTIONS_ANSWERS_FILE = "data.json"
with open(QUESTIONS_ANSWERS_FILE, encoding="utf-8") as _file:
    questions_and_answers: list[dict] = json.load(_file)


def get_random_question() -> Question:
    """
    returns a random question from the list of questions
    """

    scores = [ques["current_probability"] for ques in questions_and_answers]
    if sum(scores) == 0:
        idx = random.randint(0, len(questions_and_answers) - 1)
    else:
        idx = random.choices(range(len(questions_and_answers)), weights=scores)[0]
    ques = questions_and_answers[idx]
    ques =  Question(
        index=idx,
        question=ques["question"],
        answers=ques.get("answers", []),
        options=ques["options"],
        total_times_question_attempted=ques.get("total_times_question_attempted", 0),
        correct_times_question_attempted=ques.get("correct_times_question_attempted", 0),
        current_probability=ques.get("current_probability", 0),
    )
    idx += 1
    idx %= len(questions_and_answers)
    return ques


def update_probability(question: Question, is_correct: bool) -> Question:
    """
    updates the probability of the question based on the correctness of the answer
    """
    new_question = deepcopy(question)
    n = new_question.total_times_question_attempted
    prev_avg = new_question.current_probability * n
    if is_correct:
        new_question.current_probability = (prev_avg * 0.8) / (n + 1)
    else:
        error_factor = 0.90
        damp_avg = (prev_avg + 1) / (n + 1)
        else_score = __map_domain(0, 1 + error_factor, 0, 1, damp_avg + error_factor)
        new_question.current_probability = else_score
    new_question.total_times_question_attempted += 1
    new_question.correct_times_question_attempted += 1 if is_correct else 0
    return new_question


def update_question_in_file(question: Question):
    """
    updates the question in the json file with the given data
    """
    idx = question.index
    ques_dict = asdict(question)
    # remove the index from the dict
    ques_dict.pop("index")
    questions_and_answers[idx] = ques_dict
    # write the updated list to the file
    with open(QUESTIONS_ANSWERS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions_and_answers, f, indent=4)


def __map_domain(x1, x2, y1, y2, value):
    return y1 + (value - x1) * (y2 - y1) / (x2 - x1)
