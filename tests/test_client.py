import asyncio
import json

import pytest
from websockets.asyncio.server import serve

from greenheat import GreenHeatClient
from greenheat.models import GreenHeatMessage
from tests.test_message import make_payload


@pytest.fixture
async def server():
    paths = []

    async def handler(ws):
        paths.append(ws.request.path)
        await ws.send(json.dumps(make_payload()))
        await ws.wait_closed()

    async with serve(handler, "127.0.0.1", 0) as srv:
        port = srv.sockets[0].getsockname()[1]
        srv.base_url = f"ws://127.0.0.1:{port}/"
        srv.paths = paths
        yield srv


def make_client(server, channel, on_message, **kwargs):
    return GreenHeatClient(channel, on_message, base_url=server.base_url, **kwargs)


async def test_receives_messages(server):
    received: asyncio.Queue[GreenHeatMessage] = asyncio.Queue()

    async with make_client(server, "WolfwithSword", received.put) as client:
        msg = await asyncio.wait_for(received.get(), timeout=5)

    assert msg.twitch_id == "123456"
    assert server.paths == ["/wolfwithsword"]
    assert client.closed


async def test_closed_client(server):
    async def noop(_):
        pass

    client = make_client(server, "wolfwithsword", noop)
    async with client:
        pass

    with pytest.raises(RuntimeError):
        await client.run()


async def test_same_channel_separate_clients():
    async def noop(_):
        pass

    assert GreenHeatClient("wolfwithsword", noop) is not GreenHeatClient("wolfwithsword", noop)

async def test_diff_channel_separate_clients():
    async def noop(_):
        pass

    assert GreenHeatClient("wolfwithsword", noop) is not GreenHeatClient("just__jane", noop)


async def test_connect_timeout():
    async def noop(_):
        pass

    client = GreenHeatClient("wolfwithsword", noop, connect_timeout=0.5, base_url="ws://127.0.0.1:9/")

    with pytest.raises(asyncio.TimeoutError):
        async with client:
            pass
