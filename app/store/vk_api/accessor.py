import json
import random
import typing
from urllib.parse import urlencode, urljoin

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.bot.constants import (
    ASK_FOR_RIGHTS,
    CHOOSE_ANSWERING_COMMAND,
    GET_INFO_COMMAND,
    INFO_ABOUT_TEAM_SIZE,
    MAX_PLAYERS_IN_TEAM,
    START_GAME_COMMAND,
    STOP_GAME_COMMAND,
    STRANGE_NUM_FROM_VK,
)
from app.store.vk_api.dataclasses import (
    Message,
    Update,
    UpdateMessage,
    UpdateObject,
)
from app.store.vk_api.poller import Poller
from app.users.models import UserModel

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_PATH = "https://api.vk.com/method/"
API_VERSION = "5.131"


class VKApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)

        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.ts: int | None = None

    async def connect(self, app: "Application") -> None:
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        try:
            await self._get_long_poll_service()
        except Exception as e:
            self.logger.error("Exception", exc_info=e)

        self.poller = Poller(app.store)
        self.logger.info("start polling")
        self.poller.start()

    async def disconnect(self, app: "Application") -> None:
        if self.session:
            await self.session.close()

        if self.poller:
            self.logger.info("stop polling")
            await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        params.setdefault("v", API_VERSION)
        return f"{urljoin(host, method)}?{urlencode(params)}"

    async def _get_long_poll_service(self) -> None:
        """Запрос сервера для LongPolling,
        получает его параметры и записывает в аксессор
        """
        async with self.session.get(
                self._build_query(
                    host=API_PATH,
                    method="groups.getLongPollServer",
                    params={
                        "group_id": self.app.config.bot.group_id,
                        "access_token": self.app.config.bot.token,
                    },
                )
        ) as response:
            data = (await response.json())["response"]
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]
            self.logger.info(data)

    async def poll(self):
        """Отправляет LongPoll запрос
        и получает список обновлений класса Update
        """
        async with self.session.get(
                self._build_query(
                    host=self.server,
                    method="",
                    params={
                        "act": "a_check",
                        "key": self.key,
                        "ts": self.ts,
                        "wait": 30,
                    },
                )
        ) as response:
            data = await response.json()
            self.logger.info(data)
            self.ts = data["ts"]

            updates = [
                Update(
                    type=update["type"],
                    object=UpdateObject(
                        message=UpdateMessage(
                            id=update["object"]["message"]["id"],
                            from_id=update["object"]["message"]["from_id"],
                            text=update["object"]["message"]["text"],
                            peer_id=update["object"]["message"]["peer_id"],
                        )
                    ),
                )
                for update in data.get("updates", [])
            ]
            self.logger.info(updates)
            await self.app.store.bot_manager.handle_updates(updates)

    async def send_message(self, message: Message) -> None:
        """Позволяет отправить сообщение пользователю"""
        async with self.session.get(
                self._build_query(
                    API_PATH,
                    "messages.send",
                    params={
                        "user_id": message.user_id,
                        "random_id": random.randint(1, 2 ** 32),
                        "peer_id": f"-{self.app.config.bot.group_id}",
                        "message": message.text,
                        "access_token": self.app.config.bot.token,
                    },
                )
        ) as response:
            data = await response.json()
            self.logger.info(data)

    async def send_message_to_chat(
            self, chat_id: int, message: str, keyboard='{"buttons":[]}'
    ) -> None:
        """Позволяет отправить сообщение в конкретный чат
        Может использовать кнопки
        """
        async with self.session.get(
                self._build_query(
                    API_PATH,
                    "messages.send",
                    params={
                        "random_id": random.randint(1, 2 ** 32),
                        "chat_id": chat_id,
                        "message": message,
                        "access_token": self.app.config.bot.token,
                        "keyboard": keyboard,
                    },
                )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def get_chat_members(self, chat_id: int) -> list[UserModel]:
        """Позволяет получить участников чата в виде списка UserModel"""
        async with self.session.get(
                self._build_query(
                    API_PATH,
                    "messages.getConversationMembers",
                    params={
                        "peer_id": STRANGE_NUM_FROM_VK + chat_id,
                        "fields": "id",
                        "access_token": self.app.config.bot.token,
                    },
                )
        ) as resp:
            try:
                data = await resp.json()
                # вот это вот возвращает массив вк-объектов "пользователь"
                users = data["response"]["profiles"]
                self.logger.info(users)
                # если их больше 6, выведется сообщение и предупреждение
                if len(users) > MAX_PLAYERS_IN_TEAM:
                    await self.send_message_to_chat(
                        chat_id=chat_id, message=INFO_ABOUT_TEAM_SIZE
                    )
                return [
                    UserModel(
                        vk_id=user["id"],
                        first_name=user["first_name"],
                        last_name=user["last_name"],
                    )
                    for user in users
                ]
            # я предполагаю, что исключение будет только в том,
            # что боту без прав администратора не дадут информацию
            # data придёт пустая, и грозит KeyError
            except KeyError:
                await self.send_message_to_chat(
                    chat_id=chat_id,
                    message=ASK_FOR_RIGHTS,
                    keyboard=await self.get_game_and_info_keyboard(),
                )

    @staticmethod
    async def one_button_creater(
            text: str, color: str) -> dict:
        return {
            "action": {
                "type": "text",
                "label": text,
            },
            "color": color,
        }

    async def get_game_and_info_keyboard(self) -> str:
        keyboard = {
            "inline": True,
            "buttons": [
                [
                    await self.one_button_creater(
                        START_GAME_COMMAND, "positive"
                    ),
                    await self.one_button_creater(GET_INFO_COMMAND, "primary"),
                ],
            ],
        }
        keyboard = json.dumps(keyboard, ensure_ascii=False).encode("utf-8")
        return str(keyboard.decode("utf-8"))

    async def get_captain_game_keyboard(self) -> str:
        keyboard = {
            "inline": True,
            "buttons": [
                [
                    await self.one_button_creater(
                        text=CHOOSE_ANSWERING_COMMAND,
                        color="positive",
                    ),
                    await self.one_button_creater(
                        text=STOP_GAME_COMMAND,
                        color="secondary"),
                ]
            ],
        }
        keyboard = json.dumps(keyboard, ensure_ascii=False).encode("utf-8")
        return str(keyboard.decode("utf-8"))

    async def get_captain_choice_keyboard(self, players: list[UserModel]) -> str:
        buttons = [await self.one_button_creater(
            text=f"Отвечает {pl.first_name} {pl.last_name}",
            color="secondary"
        ) for pl in players]
        keyboard = {
            # отобразится под полем ввода сообщения
            "inline": False,
            # скроется после нажатия на кнопку
            "one_time": True,
            "buttons": [buttons],
        }
        keyboard = json.dumps(keyboard, ensure_ascii=False).encode("utf-8")
        return str(keyboard.decode("utf-8"))
