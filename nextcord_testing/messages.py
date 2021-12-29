from nextcord.core.gateway.enums import OpcodeEnum


HEARTBEAT_INTERVAL = 45000


HELLO = {
    "op": OpcodeEnum.HELLO.value,
    "d": {"heartbeat_interval": HEARTBEAT_INTERVAL},
    "s": None,
    "t": None,
}

READY = {
    "t": "READY",
    "s": 1,
    "op": 0,
    "d": {
        "v": 9,
        "user_settings": {},
        "user": {
            "verified": True,
            "mfa_enabled": True,
            "flags": 0,
            "bot": True,
            "email": None,
            "id": "111111111111111111",
            "username": "Bot",
            "discriminator": "0000",
            "avatar": "00000000000000000000000000000000",
        },
        "shard": [0, 1],
        "session_id": "1",
        "guilds": [],
        "application": {
            "id": "111111111111111111",
            "flags": 0,
        },
    },
}

HEARTBEAT_ACK = {"s": None, "t": None, "op": 11, "d": None}
