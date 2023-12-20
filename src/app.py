"""
This file contains the main app logic and Flet UI entry point.
"""
from copy import deepcopy
from functools import partial

import flet as ft
from src.quiz import Question
from src.quiz import get_random_question, update_probability, update_question_in_file


def main(page: ft.Page):
    """
    Main app logic
    """
    page.title = "AWS Solutions Architect Associate Exam Prep"

    question_data = get_random_question()
    question_header, question_body = __get_header_and_description(question_data)

    chosen_answers_list: list[int] = []
    allowed_answers = max(1, len(question_data.answers))

    if allowed_answers > 1:
        question_body += (
            f" (Choose any { 'two' if allowed_answers == 2 else 'three' } options.)"
        )

    ############################
    ###### Event Handlers ######
    ############################

    def on_option_selected(i: int, e: ft.ControlEvent | None):
        """If an option in the checkbox is selected, this function is called"""
        is_tapped_on_text = e is None
        __put_ans_in_list(i, chosen_answers_list, allowed_answers)
        __update_check_boxes_ui(i, checkboxes, chosen_answers_list, is_tapped_on_text)
        submit_button.disabled = len(chosen_answers_list) < allowed_answers
        page.update()

    def on_submit_button_click(_: ft.ControlEvent):
        """If submit button is clicked, this function is called"""
        _update_wrong_and_right_checkboxes_ui()  # Makes the right and wrong checkboxes green and red
        if len(question_data.answers) == 0:
            # If no answer is found in the question data, show an alert dialog
            # asking the user to update the answer with the current selected
            _show_update_ans_alert_dialog()
            return

        submit_button.text = "Next"
        submit_button.on_click = _go_to_next_page

        if len(question_data.answers) > 0:
            # updating the question details only if the question has an answer
            # incrementing the probability, number of tries
            _update_question_details()

        page.update()

    #######################
    ###### Util Fn's ######
    #######################

    def _go_to_next_page(_: ft.ControlEvent | None):
        page.clean()
        main(page)

    def _update_wrong_and_right_checkboxes_ui():
        for i in chosen_answers_list:
            if i in question_data.answers:
                color = ft.colors.GREEN_900
            else:
                color = ft.colors.RED_900
            checkboxes[i].fill_color = color

    def _show_update_ans_alert_dialog():
        error_msg = f"No correct answer found in question data for {question_header}"
        update_ans_btn = ft.TextButton(
            "Update Answer", on_click=_update_answer_and_get_next_page
        )
        page.show_dialog(create_err_alert_dialog(page, [update_ans_btn], error_msg))

    def _update_question_details():
        is_given_ans_correct = set(chosen_answers_list) == set(question_data.answers)
        new_ques_data = update_probability(question_data, is_given_ans_correct)
        update_question_in_file(new_ques_data)

    def _update_answer_and_get_next_page(_: ft.ControlEvent | None = None):
        new_ques_data = deepcopy(question_data)
        new_ques_data.answers = chosen_answers_list
        update_question_in_file(new_ques_data)
        page.close_dialog()
        _go_to_next_page(None)

    ###################
    ######## UI #######
    ###################

    checkboxes = []
    for i in range(len(question_data.options)):
        checkboxes.append(ft.Checkbox(on_change=partial(on_option_selected, i)))

    options_group: list[ft.Control] = [
        ft.Row(
            [
                checkboxes[i],
                *__split_text_to_widgets(
                    option, partial(on_option_selected, i), size=14
                ),
            ],
            wrap=True,  # Wrap the options to next line if the options exceed the width of the screen
        )
        for i, option in enumerate(question_data.options)
    ]

    submit_button = ft.FilledButton(
        "Submit",
        on_click=on_submit_button_click,
        disabled=len(chosen_answers_list) < allowed_answers,
    )

    page.add(
        ft.Column(
            controls=[
                ft.Text(question_header, size=28),
                ft.Text(question_body, size=18),
                ft.Container(
                    ft.Column(options_group), margin=ft.margin.only(left=20, top=10)
                ),
                ft.Container(margin=ft.margin.only(bottom=10)),
                submit_button,
            ]
        )
    )


def create_err_alert_dialog(
    page: ft.Page, more_actions: list[ft.Control], error_msg: str
) -> ft.AlertDialog:
    """
    Creates an error alert dialog
    """
    return ft.AlertDialog(
        title=ft.Text("Error"),
        content=ft.Text(error_msg),
        actions=[
            ft.Container(
                ft.Row(
                    [
                        ft.TextButton("Ok", on_click=lambda _: page.close_dialog()),
                        *more_actions,
                    ]
                ),
                margin=ft.margin.only(left=-16),
            )
        ],
    )


def __get_header_and_description(question_data: Question) -> tuple[str, str]:
    """
    Returns header and description for the question
    """
    ques = question_data.question.split("\n")
    question_header = ques[0]
    question_body = "".join(ques[1:])
    return question_header, question_body


def __put_ans_in_list(i: int, chosen_answers_list: list[int], allowed_answers: int):
    """
    Selects an answer
    """
    if i not in chosen_answers_list:
        if len(chosen_answers_list) >= allowed_answers:
            chosen_answers_list.pop(0)
        chosen_answers_list.append(i)


def __update_check_boxes_ui(
    i: int,
    checkboxes: list[ft.Checkbox],
    chosen_answers_list: list[int],
    is_tapped_on_text: bool = False,
):
    """
    Updates the checkboxes
    """
    for idx, checkbox in enumerate(checkboxes):
        if idx == i:
            if is_tapped_on_text:
                checkbox.value = not checkbox.value
            if not checkbox.value:
                chosen_answers_list.remove(i)
            continue
        if idx in chosen_answers_list:
            continue
        checkbox.value = False


def __split_text_to_widgets(text: str, click_fn, **kwargs) -> list[ft.Control]:
    """
    Breaks text into list of ft.Text widgets this is used to wrap the options to next line
    as the default ft.Text widget does not support wrapping it wraps the whole text field
    """
    return [
        ft.Container(
            ft.Text(line, **kwargs),
            margin=ft.margin.only(right=-6, top=-3, bottom=-3),
            on_click=lambda _: click_fn(None),
        )
        for line in text.replace("\n", "").split()
    ]
