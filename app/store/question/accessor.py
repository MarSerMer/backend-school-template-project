from collections.abc import Sequence

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
        Предполагается, что наличие вопроса уже проверено.
        """
        new_answer = AnswerModel(answer=answer, question_id=q_id)
        await self.app.database.add_to_database(new_answer)
        return new_answer

    async def get_question_for_bot(self, q_id: int) -> QuestionModel | None:
        """Позволяет получить вопрос по его id."""
        query = select(QuestionModel).where(QuestionModel.id == q_id)
        question = await self.app.database.select_from_database(query)
        if question:
            return question.scalar()
        return None

    async def get_question_for_view(
        self, q_id: int | None
    ) -> list[QuestionModel]:
        """Позволяет посмотреть конкретный вопрос (если передан id)
        либо посмотреть все вопросы (без ответов)
        """
        query = select(QuestionModel)
        if q_id:
            query = query.where(QuestionModel.id == q_id)
        response = await self.app.database.select_from_database(query=query)
        return response.scalars().all()

    async def get_answer_for_bot(
        self, q_id: int
    ) -> Sequence[AnswerModel] | None:
        """Позволит узнать ответ/ответы на вопрос"""
        query = select(AnswerModel).where(AnswerModel.question_id == q_id)
        res = await self.app.database.select_from_database(query=query)
        return res.scalars().all() or None

    async def question_ok(self, q_id: int) -> bool:
        """Нужна для проверки наличия ответа на вопрос."""
        query = (
            select(AnswerModel).where(AnswerModel.question_id == q_id).first()
        )
        return await self.app.database.select_from_database(query=query)

    async def get_answers_list(self, q_id: int) -> list[str]:
        """Позволяет получить список ответов на конкретный вопрос"""
        res: list = []
        if await self.get_question_for_bot(q_id=q_id):
            query = select(AnswerModel).where(AnswerModel.question_id == q_id)
            result = await self.app.database.select_from_database(query)
            answers = result.scalars().all()
            res = [a.answer for a in answers]
        return res
