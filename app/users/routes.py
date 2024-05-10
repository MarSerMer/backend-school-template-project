import typing

from app.users.views import UsersView

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    # добавить вопрос
    app.router.add_view("/all_users", UsersView)
