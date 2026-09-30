import asyncio
import argparse
from greenheat.client import GreenHeat

import logging
logger = logging.getLogger(__name__)

async def on_message(message):
    logger.debug(f"greenheat event: {message}")

parser = argparse.ArgumentParser()
parser.add_argument("--channel", required=True)
parser.add_argument("--debug", action="store_true")

args = parser.parse_args()


def main():
    assert args.channel
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    conn = GreenHeat(args.channel, on_message=on_message)
    asyncio.run(conn.run())

if __name__ == "__main__.py":
    main()
