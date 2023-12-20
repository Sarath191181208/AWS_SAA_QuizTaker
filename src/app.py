from copy import deepcopy
import flet as ft
from src.quiz import get_random_question, update_probability, update_question_in_file
from functools import partial


def main(page: ft.Page):
    page.title = "AWS Solutions Architect Associate Exam Prep"
    question_data = get_random_question()
    ques = question_data.question.split("\n")
    question_header = ques[0]
    question_body = "".join(ques[1:])

    chosen_answers_list: list[int] = []
    allowed_answers = max(1, len(question_data.answers))

    error_msg: str | None = None

    if allowed_answers > 1:
        question_body += (
            f" (Choose any { 'two' if allowed_answers == 2 else 'three' } options.)"
        )

    def on_option_selected(i: int, e: ft.ControlEvent | None):
        if i not in chosen_answers_list:
            if len(chosen_answers_list) >= allowed_answers:
                chosen_answers_list.pop(0)
            chosen_answers_list.append(i)
        for idx, checkbox in enumerate(checkboxes):
            if idx == i:
                if e is None:  # tapped on text
                    checkbox.value = not checkbox.value
                if not checkbox.value:
                    chosen_answers_list.remove(i)
                continue
            if idx in chosen_answers_list:
                continue
            checkbox.value = False
        submit_button.disabled = len(chosen_answers_list) < allowed_answers
        page.update()

    def on_next_button_click(_: ft.ControlEvent | None):
        page.clean()
        main(page)

    def __update_answer_and_refresh():
        new_ques_data = deepcopy(question_data)
        new_ques_data.answers = chosen_answers_list
        update_question_in_file(new_ques_data)
        page.close_dialog()
        on_next_button_click(None)

    def on_submit_button_click(_: ft.ControlEvent):
        for i in chosen_answers_list:
            if i in question_data.answers:
                color = ft.colors.GREEN_900
            else:
                color = ft.colors.RED_900
            checkboxes[i].fill_color = color

        if len(question_data.answers) == 0:
            error_msg = (
                f"No correct answer found in question data for {question_header}"
            )
            page.show_dialog(
                ft.AlertDialog(
                    title=ft.Text("Error"),
                    content=ft.Text(error_msg),
                    actions=[
                        ft.Container(
                            ft.Row(
                                [
                                    ft.TextButton(
                                        "Ok", on_click=lambda _: page.close_dialog()
                                    ),
                                    ft.TextButton(
                                        "Update Answer",
                                        on_click= lambda _: __update_answer_and_refresh(),
                                    ),
                                ]
                            ),
                            margin=ft.margin.only(left=-16),
                        )
                    ],
                )
            )
            return

        submit_button.text = "Next"
        submit_button.on_click = on_next_button_click

        if len(question_data.answers) > 0:
            is_correct = set(chosen_answers_list) == set(question_data.answers)
            new_ques_data = update_probability(question_data, is_correct)
            update_question_in_file(new_ques_data)

        page.update()

    checkboxes = []
    for i in range(len(question_data.options)):
        checkboxes.append(ft.Checkbox(on_change=partial(on_option_selected, i)))

    options_group = ft.Column(
        [
            ft.Row(
                [
                    checkboxes[i],
                    *split_text_to_widgets(
                        option, partial(on_option_selected, i), size=14
                    ),
                ],
                wrap=True,
            )
            for i, option in enumerate(question_data.options)
        ]
    )

    submit_button = ft.FilledButton(
        "Submit",
        on_click=on_submit_button_click,
        disabled=len(chosen_answers_list) < allowed_answers,
    )

    # show error message if any with red color and bold font
    # along with error icon
    if error_msg:
        error_msg_widget = ft.Row(
            [
                ft.Icon(ft.icons.ERROR, size=16, color=ft.colors.RED_900),
                ft.Text(error_msg, size=14, color=ft.colors.RED_900),
            ],
        )
        page.add(error_msg_widget)

    page.add(
        ft.Column(
            controls=[
                ft.Text(question_header, size=28),
                ft.Text(question_body, size=18),
                ft.Container(options_group, margin=ft.margin.only(left=20, top=10)),
                ft.Container(margin=ft.margin.only(bottom=10)),
                submit_button,
            ]
        )
    )


def split_text_to_widgets(text: str, click_fn, **kwargs) -> list[ft.Control]:
    """
    Breaks text into list of ft.Text widgets
    """
    return [
        ft.Container(
            ft.Text(line, **kwargs),
            margin=ft.margin.only(right=-6, top=-3, bottom=-3),
            on_click=lambda _: click_fn(None),
        )
        for line in text.replace("\n", "").split()
    ]
