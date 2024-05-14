import typing

from app.store.database.database import Database

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application", *args, **kwargs):
        from app.store.admin.accessor import AdminAccessor
        from app.store.bot.manager import BotManager
        from app.store.game.accessor import GameAccessor
        from app.store.question.accessor import QuestionAccessor
        from app.store.users.accessor import UserAccessor
        from app.store.vk_api.accessor import VKApiAccessor

        self.user = UserAccessor(app)
        self.vk_api = VKApiAccessor(app)
        self.admins = AdminAccessor(app)
        self.questions = QuestionAccessor(app)
        self.games = GameAccessor(app)
        self.bot_manager = BotManager(app)
        self.app = app


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
