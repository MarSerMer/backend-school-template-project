import typing

from app.store.database.database import Database

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application", *args, **kwargs):
        from app.store.admin.accessor import AdminAccessor
        from app.store.question.accessor import QuestionAccessor
        from app.store.vk_api.accessor import VKApiAccessor
        from app.users.accessor import UserAccessor

        self.user = UserAccessor(self)
        self.vk_api = VKApiAccessor
        self.admins = AdminAccessor(app)
        self.questions = QuestionAccessor(app)
