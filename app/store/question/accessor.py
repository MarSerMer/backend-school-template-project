from collections.abc import Sequence

from aiohttp.web_exceptions import HTTPNotFound
from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.question.models import AnswerModel, QuestionModel


class QuestionAccessor(BaseAccessor):
    async def create_question(self, question: str) -> QuestionModel:
        """Позволяет добавить вопрос в базу"""
        new_question = QuestionModel(question=question)
        await self.app.database.add_to_database(new_question)
        return new_question

    async def create_answer(self, q_id: int, answer: str) -> AnswerModel:
        """Позволяет добавить ответ в базу.
        Перед добавлением роверит,
        есть ли в базе вопрос с указанным id, и
        если такого нет, то raise HTTPNotFound.
        """
        if self.get_question_for_bot(q_id=q_id):
            new_answer = AnswerModel(answer=answer, question_id=q_id)
            await self.app.database.add_to_database(new_answer)
            return new_answer
        raise HTTPNotFound

    async def get_question_for_bot(self, q_id: int) -> QuestionModel | None:
        # логику выбора id нужно выпихнуть куда-нибудь не сюда
        # в бот, например, пусть он и получает все id и из них рандомом выбирает
        query = select(QuestionModel).where(QuestionModel.id == q_id)
        question = await self.app.database.select_from_database(query)
        if question:
            return question.scalar()
        return None

    async def get_question_for_view(
        self, q_id: int | None
    ) -> list[QuestionModel]:
        """Позволяет получить список вопросов (без ответов).
        Если задан id вопроса, будет искать конкретный вопрос,
        и если не найдёт, то  raise HTTPNotFound.
        Если id не задан, то выдаст все вопросы из базы.
        """
        query = select(QuestionModel)
        if q_id:
            query = query.where(QuestionModel.id == q_id)
        response = await self.app.database.select_from_database(query=query)
        return response.scalars().all()

    async def get_answer_for_bot(
        self, q_id: int
    ) -> Sequence[AnswerModel] | None:
        """Позволит узнать ответ/ответы на вопрос
        Это только для бота
        Для вью есть другая функция
        """
        query = select(AnswerModel).where(AnswerModel.question_id == q_id)
        res = await self.app.database.select_from_database(query=query)
        if res:
            return res.scalars().all
        return None

    async def question_ok(self, q_id: int) -> bool:
        """Нужна для проверки наличия ответа на вопрос.
        В игру будут попадать только те вопросы,
        на которые в базе есть хотя бы один ответ
        """
        query = (
            select(AnswerModel).where(AnswerModel.question_id == q_id).first()
        )
        return await self.app.database.select_from_database(query=query)

    async def list_answers(self, q_id: int | None):
        """Позволяет получить ответы на конкретный вопрос
        по его id (если они есть).
        Если же id не указан, то позволяет
        получить список всех вопросов и (если есть) ответов.
        """
        query = select(QuestionModel).join(
            AnswerModel, AnswerModel.question_id == q_id, isouter=True
        )
        if q_id:
            if await self.get_question_for_bot(q_id=q_id):
                query = (
                    select(QuestionModel)
                    .join(
                        AnswerModel,
                        AnswerModel.question_id == q_id,
                        isouter=True,
                    )
                    .where(QuestionModel.id == q_id)
                )
            else:
                raise HTTPNotFound
        response = await self.app.database.select_from_database(query=query)
        return response.scalars().all()

    async def get_answers_list(self, q_id: int) -> list[str]:
        res: list = []
        # res["answers"] = []
        if await self.get_question_for_bot(q_id=q_id):
            query = select(AnswerModel).where(AnswerModel.question_id == q_id)
            result = await self.app.database.select_from_database(query)
            answers = result.scalars().all()
            res = [a.answer for a in answers]
        return res
