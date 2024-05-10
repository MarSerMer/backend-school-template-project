import typing

from app.question.views import (
    AnswerAddView,
    AnswersListView,
    AnswersView,
    QuestionAddView,
    QuestionView,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    # добавить вопрос
    app.router.add_view("/add_question", QuestionAddView)
    # добавить ответ
    app.router.add_view("/add_answer", AnswerAddView)
    # посмотреть конкретный вопрос или все вопросы
    app.router.add_view("/see_q", QuestionView)
    # посмотреть конкретный вопрос и ответы на него или же
    # все вопросы и ответы на них
    app.router.add_view("/see_q_and_a", AnswersView)
    # увидеть конкретный вопрос и ответы на него
    app.router.add_view("/see_q_and_a_lst", AnswersListView)
