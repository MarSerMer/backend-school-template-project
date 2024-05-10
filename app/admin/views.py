from hashlib import sha256

from aiohttp.web_exceptions import HTTPBadRequest, HTTPForbidden
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import new_session

from app.admin.schemes import AdminSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @docs(
        tags=["Metaclass_project"],
        summary="Admin login",
        description="Allows to login admin",
    )
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        data = await self.request.json()
        try:
            email = data["email"]
            password = data["password"]
        except KeyError:
            raise HTTPBadRequest from None
        person = await self.store.admins.get_by_email(email=email)
        if person and person.password == sha256(password.encode()).hexdigest():
            raw_admin = AdminSchema().dump(person)
            session = await new_session(request=self.request)
            session["token"] = self.request.app.config.session.key
            session["admin"] = raw_admin
            return json_response(data=raw_admin)
        raise HTTPForbidden


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(tags=["Metaclass_project"], summary="Get the current admin")
    @response_schema(AdminSchema, 200)
    async def get(self):
        return json_response(data=AdminSchema().dump(self.request.admin))
