import random

from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.game.models import Game
from app.question.models import QuestionModel, AnswerModel

from app.store.bot.constants import QUESTIONS_NEEDED, MAX_PLAYERS_IN_TEAM
from app.users.models import UserModel


class GameAccessor(BaseAccessor):
    async def get_all_games(self):
        query = select(Game)
        games = await self.app.database.select_from_database(query=query)
        return games.scalars().all()

    async def create_a_new_game(self, chat_id: int, players: list) -> Game:
        """Позволяет получить новую игру"""
        players_for_game = await self.get_players_for_game(players=players)
        captain = random.choice(players_for_game)
        question_for_game = await self.get_questions_for_game()
        new_game = Game(
            chat_id=chat_id,
            captain=captain.id,
            players=players_for_game,
            questions=question_for_game,
        )
        #TODO подумать, нужно ли сразу записывать игру в базу
        # и если нужно, то тогда возвращать её с её id
        await self.app.database.add_to_database(new_game)
        return new_game

    async def get_players_for_game(self, players: list) -> list[UserModel]:
        """Позволяет получить список игроков
        Записывает в базу тех игроков, которых в ней не было"""
        if len(players) > MAX_PLAYERS_IN_TEAM:
            players = random.sample(players, k=MAX_PLAYERS_IN_TEAM)
            # всех в БД! Но после проверки того, что их там нет:
        pl_vk_ids = [pl.vk_id for pl in players]
        players_already_in_db = (
            await self.app.store.user.get_many_users_by_vk_id(vk_ids=pl_vk_ids)
        )
        if len(players_already_in_db) < len(pl_vk_ids):
            # выясняем кто остался
            players_to_add = players - players_already_in_db
            # оставшихся в БД:
            if players_to_add:
                await self.app.store.user.add_many_users_to_db(
                    users=players_to_add
                )
            # теперь можно получить уже игроков
            players_for_game = (
                await self.app.store.user.get_many_users_by_vk_id(
                    vk_ids=pl_vk_ids
                )
            )
        else:
            players_for_game = players_already_in_db
        return players_for_game.scalars().all()

    async def get_questions_for_game(self) -> list[QuestionModel]:
        """Позволяет получить список из 11 вопросов, на которые есть ответ"""
        query = select(AnswerModel.question_id)
        res = await self.app.database.select_from_database(query)
        res_i = res.scalars().all()
        q_ids = list(set(res_i))
        if len(q_ids) > QUESTIONS_NEEDED:
            q_ids = random.sample(q_ids, k=QUESTIONS_NEEDED)
        query_q = select(QuestionModel).where(QuestionModel.id.in_(q_ids))
        q_res = await self.app.database.select_from_database(query_q)
        return q_res.scalars().all()
