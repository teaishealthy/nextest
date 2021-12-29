from typing import Optional
from aiohttp.client_ws import ClientWebSocketResponse
from nextcord.core.protocols.http import HTTPClient
from nextcord.core.http import Route
from nextcord.type_sheet import TypeSheet

from .ws import FakeClientWebSocketResponse

from .logger import logger


class FakeHTTPResponse:
    def __init__(self, data: dict):
        self.data = data

    async def json(self):
        return self.data


class HTTPHandler:
    # TODO: Add the missing paths

    def __init__(self) -> None:
        pass

    def _handle_inner(self, route: Route):
        path = route.path.lower()
        if path == "/gateway/bot":
            return self.gateway_bot()

    async def handle(self, route: Route):
        return FakeHTTPResponse(self._handle_inner(route))

    def gateway_bot(self):
        return {
            "url": "wss://gateway.discord.gg",
            "shards": 1,
            "session_start_limit": {
                "total": 1000,
                "remaining": 1000,
                "reset_after": 86365545,
                "max_concurrency": 1,
            },
        }


class FakeHTTP(HTTPClient):
    def __init__(self, type_sheet: TypeSheet, token: Optional[str] = None):
        self.type_sheet = type_sheet
        self.token = token
        self.handler = HTTPHandler()

    async def request(self, route: Route, **kwargs):
        logger.debug(f"FakeHTTP.request called with route: {route.bucket}")
        return await self.handler.handle(route)

    async def get_gateway_bot(self):
        route = Route("GET", "/gateway/bot")
        return await self.request(route)

    async def ws_connect(self, url):
        logger.debug("FakeHTTP.ws_connect called")
        return FakeClientWebSocketResponse()

    async def close(self):
        pass

    async def handle_get_current_user():
        return


class FakeBucket:
    # We don't really need this class in the current implementation.
    # But it's here for future use. 
    def __init__(self, route: Route):
        logger.debug("FakeBucket.__init__ called")

    async def __aenter__(self):
        logger.debug("FakeBucket.__aenter__ called")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass
