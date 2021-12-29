import asyncio
from typing import Tuple
import zlib

from aiohttp.http_websocket import WSMsgType
from nextcord.core.gateway.enums import OpcodeEnum

from .messages import HEARTBEAT_ACK, HELLO, READY, HEARTBEAT_INTERVAL
from .logger import logger
import json


ZLIB_SUFFIX = b"\x00\x00\xff\xff"

deflator = zlib.compressobj()



class Missing:
    pass


class FakeMessage:
    def __init__(self, type: WSMsgType, data) -> None:
        # Basically "invert" the way discord sends messages to us
        # See https://discord.com/developers/docs/topics/gateway#transport-compression-transport-compression-example
        if isinstance(data, dict):
            data = json.dumps(data)
        if isinstance(data, str):
            data = data.encode("utf-8")
        self.type = type
        self.data = bytearray(deflator.compress(data))

        while res := deflator.flush(zlib.Z_FULL_FLUSH):
            self.data.extend(res)


class FakeClientWebSocketResponse:
    def __init__(self) -> None:
        self.future = asyncio.Future()
        self.able_to_send = asyncio.Event()
        self.close_code = Missing
        self.shard: Tuple[int, int] = None
        self.heartbeat_future = asyncio.Future()

    def __aiter__(self):
        return self

    async def __anext__(self):
        data = await self.future
        self.future = asyncio.Future()
        # Make sure we can await the future again
        self.able_to_send.set()
        self.able_to_send.clear()

        if data == "close":
            # FIXME: There is probably a better way to do this. But this works for now
            raise StopAsyncIteration
        elif isinstance(data, FakeMessage):
            return data

    async def heartbeat_loop(self):
        while True:
            try:
                await asyncio.wait_for(self.heartbeat_future, HEARTBEAT_INTERVAL / 1000 + 5)
                # The Shard should send a HEARTBEAT in HEARTBEAT_INTERVAL seconds
                # + 5 seconds to allow for a blocked event loop
                # If it doesn't, we close the websocket 
            except asyncio.TimeoutError:
                logger.warning(
                    "FakeGateway did not receive a heartbeat in time. Closing."
                )
                await self.close()
                return
            else:
                self.heartbeat_future = asyncio.Future()

    @property
    def closed(self):
        return self.close_code != Missing # TODO: Check if there is a better way to do this

    async def send_str(self, data):
        # simulate an error
        parsed_data: dict = json.loads(data)
        if parsed_data["op"] == OpcodeEnum.IDENTIFY:
            # If the Shard tries to IDENTIFY, we should send HELLO
            await self.hello_and_ready(parsed_data)
        elif parsed_data["op"] == OpcodeEnum.HEARTBEAT:
            # If the Shard tries to HEARTBEAT, we should send HEARTBEAT_ACK
            self.future.set_result(FakeMessage(WSMsgType.BINARY, HEARTBEAT_ACK))
            self.heartbeat_future.set_result(1)

    async def hello_and_ready(self, parsed_data):
        shard = parsed_data.get("shard")
        self.shard = shard


        self.future.set_result(FakeMessage(WSMsgType.BINARY, HELLO))
        await self.able_to_send.wait()
        # Wait for the Gateway to be able to send another message
        # So that we can send READY

        self.future.set_result(FakeMessage(WSMsgType.BINARY, READY))
        # FIXME: We currently send the shard a hardcoded value
        # We should just send it self.shard
        # See .messages.READY["d"]["shard"]
        asyncio.create_task(self.heartbeat_loop())

    async def close(self, code=None):
        logger.debug(f"FakeClientWebSocketResponse.close called with code: {code}")
        self.close_code = code
        # FIXME: This is the wrong way to do this
        # We shouldn't just echo the close code back to the client
        # But it works for now and I don't know how to fix it or what the correct close code is

        self.future.set_result("close")
