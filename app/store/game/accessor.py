from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.game.models import Game


class GameAccessor(BaseAccessor):
    async def get_all_games(self):
        query = select(Game)
        games = await self.app.database.select_from_database(query=query)
        return games.scalars().all()
