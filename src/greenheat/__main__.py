import argparse
import asyncio
import logging

from greenheat.client import GreenHeat
from greenheat.models import GreenHeatMessage

logger = logging.getLogger(__name__)


async def on_message(message: GreenHeatMessage):
    logger.debug(f"greenheat event: {message}")


def main():
    parser = argparse.ArgumentParser(prog="greenheat", description="print greenheat events for a twitch channel")
    parser.add_argument("--channel", required=True)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(levelname)s - [%(name)s] %(message)s",
    )
    logging.getLogger("websockets").setLevel(logging.INFO)

    try:
        asyncio.run(GreenHeat(args.channel, on_message=on_message).run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
