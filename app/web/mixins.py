from aiohttp.abc import StreamResponse
from aiohttp.web_exceptions import HTTPUnauthorized


class AuthRequiredMixin:
    async def _iter(self) -> StreamResponse:
        if not getattr(self.request, "admin", None):
            raise HTTPUnauthorized
        # вот так вот хочет ruff
        return await super()._iter()
        # было так:
        # return await super(AuthRequiredMixin, self)._iter()
