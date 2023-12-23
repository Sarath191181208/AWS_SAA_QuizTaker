"""
This file contains the main app logic and Flet UI entry point.
"""
from copy import deepcopy
from functools import partial
from typing import Callable
import re
import flet as ft
from src.quiz import Question
from src.quiz import get_random_question, update_probability, update_question_in_file, all_tags_list

def main(page: ft.Page):
    """
    Main entry point of the app
    """
    page.title = "AWS Solutions Architect Associate Exam Prep"

    def _on_next_page():
        app_container.clean()
        single_question = SinlgeQuestion(get_random_question(), _on_next_page)
        app_container.content = single_question
        app_container.update()


    def _on_click(_: ft.ControlEvent):
        page.clean()
        page.add(app_container)
        _on_next_page()
    
    app_container = ft.Container(margin=ft.margin.only(left=20, top=10))

    page.add(
        ft.Column(
            controls=[
                ft.Text("AWS Solutions Architect Associate Exam Prep", size=28),
                ft.Container(margin=ft.margin.only(bottom=10)),
                ft.Text(
                    re.sub(r"\s+", " ", """
                    This app is designed to help you prepare for the AWS Solutions Architect Associate Exam.
                    It contains 200 questions and you can choose to answer any number of questions.
                    The app will keep track of your progress and show you the questions that you have answered incorrectly more often.
                    """),
                    size=18,
                ),
                ft.Container(margin=ft.margin.only(bottom=10)),
                ft.FilledButton("Start", on_click=_on_click),
            ]
        )
    ) 

class SinlgeQuestion(ft.UserControl):
    def __init__(self, question: Question, next_page_callback: Callable[[], None], is_editable: bool = False):
        self.question = question
        self.chosen_answers_list: list[int] = []
        self.allowed_answers = max(1, len(question.answers))
        self.next_page_callback = next_page_callback
        self.is_editable = is_editable
        super().__init__()

    def build(self):
        ques_header, ques_body = self.get_header_and_description()
        # is_editable = self.is_editable

        self.checkboxes = []
        for i in range(len(self.question.options)):
            self.checkboxes.append(ft.Checkbox(on_change=partial(self.on_option_selected, i)))

        options_group: list[ft.Control] = [
            ft.Row(
                [
                    self.checkboxes[i],
                    *self.__split_text_to_widgets(
                        option, partial(self.on_option_selected, i), size=14
                    ),
                ],
                wrap=True,  # Wrap the options to next line if the options exceed the width of the screen
            )
            for i, option in enumerate(self.question.options)
        ]

        self.submit_button = ft.FilledButton(
            "Submit",
            on_click=self.on_submit_button_click,
            disabled=len(self.chosen_answers_list) < self.allowed_answers,
        )

        self.tags_view = []
        self.header_row: ft.Control = ft.Row([ 
            ft.Text(ques_header, size=28), 
            ft.Row(self.tags_view, wrap=True),
            ft.IconButton(
                icon=ft.icons.NEW_LABEL, on_click=self.show_add_tag_dialog
            ),
        ])
        self.update_tags_view()

        return ft.Column(
            controls=[
                self.header_row,
                ft.Text(ques_body, size=18),
                ft.Container(
                    ft.Column(options_group), margin=ft.margin.only(left=20, top=10)
                ),
                ft.Container(margin=ft.margin.only(bottom=10)),
                self.submit_button,
            ]
        )

    def delete_tag(self, tag: str, _: ft.ControlEvent | None):
        self.question.tags.remove(tag)
        update_question_in_file(self.question)
        self.update_tags_view()
        self.update()
        if self.page is not None:
            self.page.update()

    def update_tags_view(self):
        self.tags_view: list[ft.Control] = [
            ft.Chip(ft.Text(tag), on_delete=partial(self.delete_tag, tag))  for tag in self.question.tags
        ]
        header: ft.Row = self.header_row # type: ignore
        header.controls[1] = ft.Row(self.tags_view, wrap=True)

    def show_add_tag_dialog(self, _: ft.ControlEvent):
        """
        Shows a dialog to add a new tag to the question
        """
        def _on_click(_: ft.ControlEvent):
            tag = tag_input.value
            if tag is None: 
                return 
            if tag in self.question.tags:
                return 
            assign_tag(tag)

        def assign_tag(tag:str):
            self.question.tags.append(tag)
            update_question_in_file(self.question)
            self.update_tags_view()
            self.update()
            if self.page is not None:
                self.page.close_dialog()
                self.page.update()

        def change_input(tag: str, _: ft.ControlEvent):
            tag_input.value = tag
            dialog.update()

        tag_input = ft.TextField()
        tags_list: list[ft.Control] = [ ft.TextButton(tag, on_click=partial(change_input, tag) ) for tag in all_tags_list ]
        dialog = ft.AlertDialog(
            title=ft.Text("Add new tag"),
            content=ft.Column(
                tight=True,
                scroll=ft.ScrollMode.ALWAYS,
                controls=[
                    ft.Text("Enter the new tag"),
                    tag_input,
                    ft.Container(margin=ft.margin.only(bottom=10)),
                    ft.FilledButton("Add", on_click=_on_click),
                    ft.Row(tags_list, wrap=True),
                ]
            ),
        )
        if self.page is not None:
            self.page.show_dialog(dialog)
    
    def get_header_and_description(self):
        global __get_header_and_description
        header_text, body = self.__get_header_and_description(self.question)
        if self.allowed_answers > 1:
            body += (
                f" (Choose any { 'two' if self.allowed_answers == 2 else 'three' } options.)"
            )
        return header_text, body

    def on_option_selected(self, i: int, e: ft.ControlEvent | None):
        """If an option in the checkbox is selected, this function is called"""
        is_tapped_on_text = e is None
        self.__put_ans_in_list(i, self.chosen_answers_list, self.allowed_answers)
        self.__update_check_boxes_ui(i, self.checkboxes, self.chosen_answers_list, is_tapped_on_text)
        self.submit_button.disabled = len(self.chosen_answers_list) < self.allowed_answers
        self.update()

    def on_submit_button_click(self, _: ft.ControlEvent):
        """If submit button is clicked, this function is called"""
        self.update_wrong_and_right_checkboxes_ui()
        if len(self.question.answers) == 0:
            # If no answer is found in the question data, show an alert dialog
            # asking the user to update the answer with the current selected
            self.show_update_ans_alert_dialog()

        self.submit_button.text = "Next"
        self.submit_button.on_click = self.go_to_next_page
    
        if len(self.question.answers) > 0:
            self.update_question_details()
        self.update()

    def update_wrong_and_right_checkboxes_ui(self):
        for i in self.question.answers:
            color = ft.colors.GREEN_900
            self.checkboxes[i].fill_color = color
        for i in self.chosen_answers_list:
            if i not in self.question.answers:
                self.checkboxes[i].fill_color = ft.colors.RED_900

    def show_update_ans_alert_dialog(self):
        error_msg = f"No correct answer found in question data for {self.question.index}"
        update_ans_btn = ft.TextButton(
            "Update Answer", on_click=self.update_answer_and_get_next_page
        )
        page = self.page
        if page is not None:
            page.show_dialog(self.create_err_alert_dialog(page, [update_ans_btn], error_msg))

    def update_question_details(self):
        is_correct = set(self.chosen_answers_list) == set(self.question.answers)
        new_data = update_probability(self.question, is_correct)
        update_question_in_file(new_data)

    def update_answer_and_get_next_page(self, _: ft.ControlEvent | None = None):
        new_ques_data = deepcopy(self.question)
        new_ques_data.answers = self.chosen_answers_list
        update_question_in_file(new_ques_data)
        page = self.page
        if page is not None:
            page.close_dialog()
        self.go_to_next_page(None)

    def go_to_next_page(self, _: ft.ControlEvent | None):
        self.next_page_callback()

    def create_err_alert_dialog(
        self,
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


    def __get_header_and_description(self, question_data: Question) -> tuple[str, str]:
        """
        Returns header and description for the question
        """
        ques = question_data.question.split("\n")
        question_header = ques[0]
        question_body = re.sub(r'\s+', " ", r" ".join(ques[1:]))
        return question_header, question_body


    def __put_ans_in_list(self, i: int, chosen_answers_list: list[int], allowed_answers: int):
        """
        Selects an answer
        """
        if i not in chosen_answers_list:
            if len(chosen_answers_list) >= allowed_answers:
                chosen_answers_list.pop(0)
            chosen_answers_list.append(i)


    def __update_check_boxes_ui(
        self,
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


    def __split_text_to_widgets(self, text: str, click_fn, **kwargs) -> list[ft.Control]:
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
