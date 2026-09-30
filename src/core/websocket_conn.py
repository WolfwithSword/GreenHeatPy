import asyncio
import ssl
from collections.abc import Awaitable, Callable

from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed

import logging
logger = logging.getLogger(__name__)

MessageCallback = Callable[[str | bytes], Awaitable[None]]

def _default_ssl_context() -> ssl.SSLContext:
    try:
        import truststore
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except ImportError:
        return ssl.create_default_context()


class WebSocketClient:
    """a generic websocket client connection supporting reads and writes

    Args:
        url: the full url to connect to including the protocol, e.g. ws://localhost:6967
        on_message: a callback to execute whenever a new message is read from the connection
        ssl_context: optional SSL context for wss:// urls; defaults to the OS trust store via truststore
    """

    def __init__(self, url: str, on_message: MessageCallback,
                 ssl_context: ssl.SSLContext | None = None):
        self.url = url
        self.on_message = on_message
        self.ssl_context = (
            (ssl_context or _default_ssl_context())
            if url.startswith("wss://")
            else None
        )

        self.websocket: ClientConnection | None = None
        self.running = True
        self.connected = asyncio.Event()

    async def run(self) -> None:
        while self.running:
            try:
                async with connect(self.url, ssl=self.ssl_context) as websocket:
                    self.websocket = websocket
                    self.connected.set()

                    try:
                        async for message in websocket:
                            await self.on_message(message)
                            if not self.running:
                                break
                    except ConnectionClosed:
                        if not self.running:
                            break
                        logger.warning(f"{self.url}: disconnected, reconnecting...")
                    finally:
                        self.websocket = None
                        self.connected.clear()

            except asyncio.CancelledError:
                raise
            except ssl.SSLCertVerificationError:
                logger.error(f"{self.url}: certificate verification failed")
                raise
            except Exception as e:
                if not self.running:
                    break
                logger.warning(f"{self.url}: connection failed ({e}), retrying...")
                await asyncio.sleep(2)

    async def wait_until_connected(self):
        await self.connected.wait()

    async def send(self, message: str | bytes) -> None:
        await self.wait_until_connected()
        if self.websocket is None:
            raise RuntimeError("WebSocket isn't connected")

        await self.websocket.send(message)

    async def close(self) -> None:
        self.running = False

        if self.websocket is not None:
            await self.websocket.close()
