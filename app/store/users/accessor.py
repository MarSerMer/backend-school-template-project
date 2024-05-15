from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.users.models import UserModel


class UserAccessor(BaseAccessor):
    async def get_all_users(self):
        query = select(UserModel)
        result = await self.app.database.select_from_database(query=query)
        return result.scalars().all()

    async def get_user_by_vk_id(self, vk_id: int) -> UserModel | None:
        query = select(UserModel).where(UserModel.vk_id == vk_id)
        res = await self.app.database.select_from_database(query=query)
        return res.scalar()

    async def add_user_to_db(
        self, vk_id: int, first_name: str, last_name: str
    ) -> None:
        if not await self.get_user_by_vk_id(vk_id=vk_id):
            user = UserModel(
                vk_id=vk_id, first_name=first_name, last_name=last_name
            )
            await self.app.database.add_to_database(user)

    async def add_many_users_to_db(self, users: list[UserModel]):
        await self.app.database.add_to_database(users)

    async def get_many_users_by_vk_id(
        self, vk_ids: list[int]
    ) -> list[UserModel] | None:
        query = select(UserModel).where(UserModel.vk_id.in_(vk_ids))
        res = await self.app.database.select_from_database(query)
        users = res.scalars().all()
        users_listed = list(users)
        return users_listed or None
