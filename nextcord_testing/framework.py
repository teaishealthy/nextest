from typing import Type
from nextcord.client.client import Client
from nextcord.type_sheet import TypeSheet
from nextcord.core.http import Bucket
from .http import FakeHTTP, FakeBucket
from .gateway import FakeGateway

from typing import TypeVar

T = TypeVar("T")


class Framework:
    type_sheet = TypeSheet(
        http_client=FakeHTTP,
        gateway=FakeGateway,
        http_bucket=Bucket
        # currently there is no reason to use a fake bucket
    )

    def __init__(self, client: Client) -> None:
        self.client = client
        self.guilds = []

    @classmethod
    def default(cls: Type[T], *args, **kwargs) -> T:
        """Takes in a uninitialised client and returns a client with a fake http client and a fake gateway"""
        kwargs["type_sheet"] = cls.type_sheet

        client = Client(*args, **kwargs)
        return cls(client)

    @classmethod
    def modify(cls: Type[T], client: Client) -> T:
        """Modifies the client state to use FakeHTTP and FakeGateway"""
        client.state.gateway = cls.type_sheet.gateway(client.state)
        client.state.http = cls.type_sheet.http_client(client.state)
        return cls(client)

    def run(self, *args, **kwargs) -> None:
        self.client.run(*args, **kwargs)
