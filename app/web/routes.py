from aiohttp.web_app import Application

__all__ = ("setup_routes",)


def setup_routes(application: Application):
    from app.admin.routes import setup_routes as admin_setup_routes
    from app.question.routes import setup_routes as question_setup_routes
    from app.users.routes import setup_routes as users_setup_routes

    admin_setup_routes(application)
    question_setup_routes(application)
    users_setup_routes(application)
