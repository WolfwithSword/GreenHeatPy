import asyncio
import logging
from collections.abc import Awaitable, Callable

from ._websocket import WebSocketClient
from .models import GreenHeatMessage

logger = logging.getLogger(__name__)

MessageHandler = Callable[[GreenHeatMessage], Awaitable[None]]


class GreenHeat:
    """creates a greenheat wss connection

    Args:
        channel: the twitch channel name to connect to
        on_message: an async callback executed for every message received
        connect_timeout: seconds to wait for the initial connection before giving up, optional
        base_url: override the greenheat server url, optional
    """

    base_url: str = "wss://heat.prod.kr/"

    def __init__(self, channel: str, on_message: MessageHandler, connect_timeout: float = 30,
                 base_url: str | None = None):
        if base_url is not None:
            self.base_url = base_url
        self.channel = channel.lower()
        self.connect_timeout = connect_timeout
        self._closed = False
        self._task: asyncio.Task | None = None

        def callback(message: str | bytes):
            return on_message(GreenHeatMessage(message))

        self.ws = WebSocketClient(self.url, callback)

    @property
    def url(self) -> str:
        return f"{self.base_url}{self.channel}"

    @property
    def closed(self) -> bool:
        return self._closed

    async def run(self) -> None:
        """connect and receives messages until closed"""
        if self._closed:
            raise RuntimeError("GreenHeat client was closed and cannot be run again")

        logger.info(f"connecting to greenheat with url: {self.ws.url}")

        task = asyncio.create_task(self.ws.run())
        try:
            await asyncio.wait_for(self.ws.wait_until_connected(), timeout=self.connect_timeout)
            logger.info(f"greenheat connected to {self.channel}")
            await task
        except asyncio.TimeoutError:
            logger.warning("greenheat connection timed out")
            raise
        finally:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    async def wait_until_connected(self) -> None:
        await self.ws.wait_until_connected()

    async def close(self) -> None:
        """closes the connection and client"""
        self._closed = True
        await self.ws.close()

    async def __aenter__(self) -> "GreenHeat":
        self._task = asyncio.create_task(self.run())
        connected = asyncio.create_task(self.ws.wait_until_connected())
        await asyncio.wait({self._task, connected}, return_when=asyncio.FIRST_COMPLETED)
        if self._task and self._task.done():
            connected.cancel()
            self._task.result()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()
        if self._task is not None and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
