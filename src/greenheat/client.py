import asyncio
from collections.abc import Awaitable, Callable

from core.websocket_conn import WebSocketClient
from greenheat.models import GreenHeatMessage

import logging
logger = logging.getLogger(__name__)

class GreenHeat:
    """creates a greenheat wss connection

    Args:
        channel: the twitch channel name to connect to
    """

    base_url: str = "wss://heat.prod.kr/"
    connections: dict[str,"GreenHeat"] = {}

    def __init__(self, channel: str, on_message: Callable[[GreenHeatMessage], Awaitable[None]]):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        self.channel = channel.lower()

        def callback(message: str | bytes):
            return on_message(GreenHeatMessage(message))

        self.ws = WebSocketClient(
            self.url,
            callback,
        )

        self.connections[self.channel] = self

    def __new__(cls, channel: str, on_message: Callable[[GreenHeatMessage], Awaitable[None]]):
        if channel.lower() in cls.connections:
            return cls.connections[channel.lower()]
        return super().__new__(cls)

    @property
    def url(self):
        return f"{self.base_url}{self.channel}"

    async def run(self):
        logger.info("connecting to greenheat with url: " + self.ws.url)

        task = asyncio.create_task(self.ws.run())
        try:
            await asyncio.wait_for(self.ws.wait_until_connected(), timeout=10)
            logger.info(f"greenheat connected to {self.channel}")
            await task
        except asyncio.TimeoutError:
            logger.warning("greenheat connection timed out")
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            raise

    async def close(self):
        await self.ws.close()
        del self.connections[self.channel]
