from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.users.models import UserModel


class UserAccessor(BaseAccessor):
    async def get_all_users(self):
        query = select(UserModel)
        result = await self.app.database.select_from_database(query=query)
        return result.scalars().all()
