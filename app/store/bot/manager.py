import typing
from logging import getLogger

from app.store.bot.constants import (
    CAP_BUTTONS_COMMENT,
    CHOOSE_ANSWERING_COMMAND,
    GET_INFO_COMMAND,
    GREETING_TEXT,
    INFO_TEXT,
    START_COMMAND,
    START_GAME_COMMAND,
    STOP_GAME_COMMAND,
    STRANGE_NUM_FROM_VK,
)
from app.store.vk_api.dataclasses import Update

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
                chat_id = update.object.message.peer_id - STRANGE_NUM_FROM_VK
                if update.object.message.payload.isdigit() and \
                        update.object.message.from_id == \
                        int(update.object.message.payload):
                    if mess == CHOOSE_ANSWERING_COMMAND:
                        await self.app.store.vk_api.send_message_to_chat(
                            chat_id=chat_id,
                            message=CAP_BUTTONS_COMMENT,
                            keyboard=await \
                                self.app.store.vk_api.get_captain_choise_keyboard(
                                    # TODO оформить кнопки с именами игроков
                                )
                        )
                elif mess == START_COMMAND:
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
                        await self.app.store.vk_api.get_chat_members(
                            chat_id=chat_id
                        )
                    )
                    # get_chat_members может и ничего не вернуть,
                    # если у бота не будет прав администратора.
                    # в таком случае get_chat_members отправит сообщение
                    # и клавиатуру снова
                    if players:
                        game = await self.app.store.games.create_a_new_game(
                            chat_id=chat_id,
                            players=players
                        )
                        self.logger.info(game)
                        self.logger.info(game.captain)
                        cap = await self.app.store.user.get_user_by_id(
                            db_id=game.captain.id
                        )
                        self.logger.info(cap)
                        captain: str = cap.first_name + " " + cap.last_name
                        self.logger.info(captain)
                        # можно попробовать вопрос из game
                        # вытаскивать по идексу,
                        # а индекс = сумма полученных очков
                        ind_q: int = game.bot_count + game.players_count
                        # ques = await self.app.store.questions.get_question_for_bot(
                        #     q_id=game.questions[ind_q]
                        # )
                        question: str = game.questions[ind_q].question
                        self.logger.info(question)
                        await self.app.store.vk_api.send_message_to_chat(
                            chat_id=chat_id,
                            message=f"Капитан: {captain}",
                            keyboard='{"buttons":[]}'
                        )
                        await self.app.store.vk_api.send_message_to_chat(
                            chat_id=chat_id,
                            message=f"Внимание, вопрос: {question}",
                            keyboard='{"buttons":[]}'
                        )
                        await self.app.store.vk_api.send_message_to_chat(
                            chat_id=chat_id,
                            message=CAP_BUTTONS_COMMENT,
                            keyboard=await \
                                self.app.store.vk_api.get_captain_game_keyboard(
                                    cap_vk_id=cap.vk_id
                                )
                        )
                        # TODO переделать или снести,
                        #  т.к. тут нет передачи данных
                        # TODO разобраться, как таскать данные туда-сюда
                elif mess == STOP_GAME_COMMAND:
                    # взять игру и записать в БД результат и
                    # поставить флаг, что она окончена
                    pass
                elif mess == CHOOSE_ANSWERING_COMMAND:
                    # кнопки, кнопки с именами!
                    # ну и дальше действия по ответу
                    pass
