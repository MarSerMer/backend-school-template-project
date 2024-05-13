import random

from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.game.models import Game
from app.question.models import QuestionModel


class GameAccessor(BaseAccessor):
    async def get_all_games(self):
        query = select(Game)
        games = await self.app.database.select_from_database(query=query)
        return games.scalars().all()

    async def create_a_new_game(self, chat_id: int, players: list) -> Game:
        # если начали игру, то понеслась-поплыли:
        # - получить список игроков - это к vk_api accessor
        # - выбрать из них капитана (случайно, это ТЗ) - прямо тут на месте
        # - всех прогнать через базу - через user accessor
        # - завести новую игру - экземпляр
        # - выбрать вопрос и внести его в игру в БД ->
        # - game.questions.append(question)
        # - всё это делать в GameAccessor, оттуда вернуть капитана и game_id
        # - объявить капитана и задать вопрос
        if len(players) > 6:
            # тут случайный выбор 6 игроков:
            players = random.sample(players, k=6)
            # всех в БД! Но после проверки того, что их там нет:
        for pl in players:
            if not await self.app.store.user.get_user_by_vk_id(vk_id=pl.vk_id):
                await self.app.store.user.add_user_to_db(
                    vk_id=pl.vk_id,
                    first_name=pl.first_name,
                    last_name=pl.last_name,
                )
        players_for_game = [
            await self.app.store.user.get_user_by_vk_id(vk_id=pl.vk_id)
            for pl in players
        ]
        captain = random.choice(players)
        # теперь время заняться вопросами
        # get_question_for_view() вернёт список всех вопросов из базы
        questions: list[
            QuestionModel
        ] = await self.app.store.questions.get_question_for_view()
        # отсекаются вопросы без ответов
        questions_ok = [
            q
            for q in questions
            if await self.app.store.questions.question_ok(q_id=q.id)
        ]
        # из вопросов с ответами выбираются 11 штук
        question_for_game = random.sample(questions_ok, k=11)
        return Game(
            chat_id=chat_id,
            captain=captain.id,
            players=players_for_game,
            questions=question_for_game,
        )
