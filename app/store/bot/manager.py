import random
import typing
from logging import getLogger

from sqlalchemy import select

from app.game.models import Game
from app.store.bot.constants import (
    ASK_FOR_RIGHTS,
    CHOOSE_ANSWERING_COMMAND,
    GET_INFO_COMMAND,
    GREETING_TEXT,
    INFO_TEXT,
    START_GAME_COMMAND,
    STOP_GAME_COMMAND,
)
from app.store.vk_api.dataclasses import Message, Update
from app.users.models import UserModel

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("Bot Manager")

    async def handle_updates(self, updates: list[Update]):
        if updates:
            for update in updates:
                mess = update.object.message.text.split("] ")[-1]
                chat_id = update.object.message.peer_id - 2000000000
                if mess == "/start":
                    await self.app.store.vk_api.send_message_to_chat(
                        message=GREETING_TEXT,
                        chat_id=chat_id,
                        keyboard=await
                        self.app.store.vk_api.get_game_and_info_keyboard(),
                    )
                elif mess == GET_INFO_COMMAND:
                    await self.app.store.vk_api.send_message_to_chat(
                        message=INFO_TEXT,
                        chat_id=chat_id,
                        keyboard=await
                        self.app.store.vk_api.get_game_and_info_keyboard(),
                    )
                elif mess == START_GAME_COMMAND:
                    # нужно составить список игроков и завести новую игру
                    players = (
                        await self.app.store.vk_api.get_chat_members_online(
                            chat_id=chat_id
                        )
                    )
                    # get_chat_members может и ничего не вернуть, если у бота не будет прав администратора.
                    if not players:
                        # клавиатуру get_chat_members отправит, так что тут pass
                        pass
                    else:
                        game = await self.app.store.games.create_a_new_game(
                            chat_id=chat_id
                        )
                        # TODO, объявить капитана, выбрать и задать вопрос
                        # TODO разобраться, как таскать данные туда-сюда
