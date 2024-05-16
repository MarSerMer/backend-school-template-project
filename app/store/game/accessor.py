import random

from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.game.models import Game, GameDataclass
from app.question.models import AnswerModel, QuestionModel
from app.store.bot.constants import MAX_PLAYERS_IN_TEAM, QUESTIONS_NEEDED
from app.users.models import UserModel


class GameAccessor(BaseAccessor):
    async def get_all_games(self):
        query = select(Game)
        games = await self.app.database.select_from_database(query=query)
        return games.scalars().all()

    async def create_a_new_game(self, chat_id: int, players: list) \
            -> GameDataclass:
        """Позволяет получить новую игру"""
        players_for_game = await self.get_players_for_game(players=players)
        captain = random.choice(players_for_game)
        questions_for_game = await self.get_questions_for_game()
        new_game = Game(
            chat_id=chat_id,
            captain=captain.id,
            players=players_for_game,
            questions=questions_for_game,
        )
        # игра записывается в базу и возвращается оттуда
        current_game = await self.app.database.add_game_with_return(new_game)
        return GameDataclass(
            id=current_game.id,
            chat_id=current_game.chat_id,
            captain=captain,
            players=players_for_game,
            finished=current_game.finished,
            winner=current_game.winner,
            players_count=current_game.players_count,
            bot_count=current_game.bot_count,
            questions=questions_for_game
        )

    async def get_players_for_game(self, players: list) -> list[UserModel]:
        """Позволяет получить список игроков
        Записывает в базу тех игроков, которых в ней не было
        """
        if len(players) > MAX_PLAYERS_IN_TEAM:
            players = random.sample(players, k=MAX_PLAYERS_IN_TEAM)
        # всех в БД! Но после проверки того, что их там нет:
        pl_vk_ids = [pl.vk_id for pl in players]
        self.logger.info(pl_vk_ids)
        players_already_in_db = (
            await self.app.store.user.get_many_users_by_vk_id(vk_ids=pl_vk_ids)
        )
        if not players_already_in_db:
            players_to_add = players
        elif len(players_already_in_db) < len(pl_vk_ids):
            players_to_add = [pl for pl in players
                              if pl not in players_already_in_db]
        else:
            players_to_add = None
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
        return players_for_game

    async def get_questions_for_game(self) -> list[QuestionModel]:
        """Позволяет получить список из 11 вопросов, на которые есть ответ"""
        query = select(AnswerModel.question_id).distinct()
        res = await self.app.database.select_from_database(query)
        res_i = res.scalars().all()
        q_ids = list(res_i)
        if len(q_ids) > QUESTIONS_NEEDED:
            q_ids = random.sample(q_ids, k=QUESTIONS_NEEDED)
        query_q = select(QuestionModel).where(QuestionModel.id.in_(q_ids))
        q_res = await self.app.database.select_from_database(query_q)
        return q_res.scalars().all()
