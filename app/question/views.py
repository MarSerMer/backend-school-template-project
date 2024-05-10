from aiohttp.web_exceptions import HTTPBadRequest, HTTPNotFound
from aiohttp_apispec import (
    docs,
    querystring_schema,
    request_schema,
    response_schema,
)

from app.question.schemes import (
    AnswerSchema,
    QuestionAnswerSchema,
    QuestionIdSchema,
    QuestionSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class QuestionAddView(AuthRequiredMixin, View):
    @docs(
        tags=["Metaclass_project"],
        summary="Question add",
        description="Allows to add a new question",
    )
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema, 200)
    async def post(self):
        q = self.data["question"]
        new_q = await self.request.app.store.questions.create_question(
            question=q
        )
        return json_response(data=QuestionSchema().dump(new_q))


class AnswerAddView(AuthRequiredMixin, View):
    @docs(
        tags=["Metaclass_project"],
        summary="Answer add",
        description="Allows to add a new answer",
    )
    @request_schema(AnswerSchema)
    @response_schema(AnswerSchema, 200)
    async def post(self):
        a = self.data["answer"]
        q_id = self.data["question_id"]
        new_a = await self.request.app.store.questions.create_answer(
            answer=a, q_id=q_id
        )
        # важно: наличие соответствующего вопроса проверяет аксессор!
        # если что, он raise HTTPNotFound
        # и уж если мы вернулись сюда, то вопрос такой в базе есть!
        return json_response(data=AnswerSchema().dump(new_a))


class QuestionView(AuthRequiredMixin, View):
    """Позволяет посмотреть конкретный вопрос (без ответа)
    или же все вопросы (без ответов)
    """

    @docs(
        tags=["Metaclass_project"],
        summary="See a question or all of them",
        description="Allows see a question by id or see all of them",
    )
    @querystring_schema(QuestionIdSchema)
    async def get(self):
        q_id = self.request.query.get("q_id")
        if q_id:
            q_id = int(q_id)
            if not await self.store.questions.get_question_for_bot(q_id=q_id):
                raise HTTPNotFound
        questions = await self.store.questions.get_question_for_view(q_id=q_id)
        result = [QuestionSchema().dump(q) for q in questions]
        return json_response(data={"questions": result})


class AnswersView(AuthRequiredMixin, View):
    # предполагается, что если в строке запроса есть id вопроса,
    # то функция должна отдать только этот вопрос и его ответ/ответы
    # либо, если такого вопроса нет, то аксессор raise HTTPNotFound.
    # если id вопроса отсутствует, то функция должна
    # выдать все вопросы и ответы на них
    # логика в аксессоре
    @docs(
        tags=["Metaclass_project"],
        summary="See answers to question or all questions and answers",
        description="Allows to see answers to question "
        "or all questions and answers",
    )
    @querystring_schema(QuestionIdSchema)
    @response_schema(QuestionAnswerSchema)
    async def get(self):
        q_id = self.request.query.get("q_id")
        if q_id:
            q_id = int(q_id)
            if not await self.store.questions.get_question_for_bot(q_id=q_id):
                raise HTTPNotFound
        answers = await self.store.questions.list_answers(q_id=q_id)
        res = [QuestionAnswerSchema().dump(ans) for ans in answers]
        # TODO почему-то не выдаёт собственно ответы,
        #  хотя join работает (см. скрин)
        return json_response(data={"questions and answers": res})


class AnswersListView(AuthRequiredMixin, View):
    """В этой функции получаем ответы на вопрос в виде списка.
    Функция должна выцепить id вопроса из адресной строки
    """

    @docs(
        tags=["Metaclass_project"],
        summary="See answers to question",
        description="Allows to see answers to question",
    )
    @querystring_schema(QuestionIdSchema)
    async def get(self):
        q_id = self.request.query.get("q_id")
        if not q_id:
            raise HTTPBadRequest
        q_id = int(q_id)
        if not await self.store.questions.get_question_for_bot(q_id=q_id):
            raise HTTPNotFound
        q = await self.store.questions.get_question_for_view(q_id=q_id)
        answers = await self.store.questions.get_answers_list(q_id=q_id)
        data = {"question": f"{q[0].question}", "answers": answers}
        return json_response(data=data)
