# from aiohttp_apispec import docs, response_schema
#
# from app.web.app import View
# from app.web.mixins import AuthRequiredMixin
# from app.web.utils import json_response
#
#
# class GameView(AuthRequiredMixin, View):
#     @docs(
#         tags=["Metaclass_project"],
#         summary="All users",
#         description="Allows to see the list of users",
#     )
#     @response_schema(GamesListSchema)
#     async def get_all_games(self):
#         res = await self.store.games.get_all_games()
#         return json_response(data=GamesListSchema().dump({"games":res}))
