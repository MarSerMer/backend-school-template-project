import typing
from hashlib import sha256

from sqlalchemy import select

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        await super().connect(app)
        if not await self.get_by_email(self.app.config.admin.email):
            await self.create_admin(
                self.app.config.admin.email, self.app.config.admin.password
            )

    async def disconnect(self, app: "Application"):
        await super().disconnect(app)

    async def get_by_email(self, email: str) -> Admin | None:
        query = select(AdminModel).where(AdminModel.email == email)
        result = await self.app.database.select_from_database(query=query)
        adm = result.scalar()
        if adm:
            return adm
        return None

    async def create_admin(self, email: str, password: str):
        if not await self.get_by_email(email):
            admin = AdminModel(
                email=email, password=sha256(password.encode()).hexdigest()
            )
            await self.app.database.add_to_database(admin)
            # return admin
