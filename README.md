# greenheat-py

A Python library for [GreenHeat](https://heat.prod.kr/), letting you receive viewer clicks, hovers and drags on your Twitch stream as async events.

## Install

```sh
pip install greenheat-py
```

## Usage

```python
import asyncio

from greenheat import GreenHeatClient
from greenheat.models import GreenHeatMessage
from greenheat.enums import GreenHeatButtonType, GreenHeatEventType


async def on_message(message: GreenHeatMessage):
    if message.type != GreenHeatEventType.CLICK:
        return

    click_action = ""
    if message.button == GreenHeatButtonType.LEFT and message.shift:
        click_action = "shift + left click"
    elif message.button == GreenHeatButtonType.RIGHT and (message.ctrl or message.alt):
        click_action = "ctrl/alt + right click"

    user = message.twitch_id or "anonymous"

    x, y = message.screen_position(1920, 1080)
    print(f"{user} clicked at ({x}, {y}) [{click_action}]")

    if message.is_in_box(0.0, 0.0, 0.5, 0.5):
        print("...in the top-left quadrant of the screen")


async def main():
    async with GreenHeatClient("wolfwithsword", on_message) as client:
        await asyncio.Event().wait()

    # Alternative
    # await client.run()

asyncio.run(main())
```

You can also run the client with `await client.run()`, which blocks until `client.close()` is called or the program is exited.

There's also a small command line tool that logs events for a channel:

```sh
greenheat --channel wolfwithsword --debug
```

## License

MIT
