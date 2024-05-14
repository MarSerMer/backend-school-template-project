from aiohttp_apispec import docs, response_schema

from app.users.schema import UsersListSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class UsersView(AuthRequiredMixin, View):
    @docs(
        tags=["Metaclass_project"],
        summary="All users",
        description="Allows to see the list of users",
    )
    @response_schema(UsersListSchema)
    async def get(self):
        res = await self.store.user.get_all_users()
        return json_response(data=UsersListSchema().dump({"users": res}))
