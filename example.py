import asyncio
import argparse

from greenheat.models import GreenHeatMessage
from greenheat import GreenHeatClient

import logging
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--channel", required=True)
parser.add_argument("--debug", action="store_true")

args = parser.parse_args()

async def on_message(message: GreenHeatMessage):
    logger.debug(f"greenheat event: {message.to_dict()}")

async def run():
    client = GreenHeatClient(args.channel, on_message)
    greenheat_run_task = asyncio.create_task(client.run())
    try:
        tasks = asyncio.gather(greenheat_run_task)
        await tasks
    finally:
        for t in (greenheat_run_task,):
            t.cancel()
        await asyncio.gather(greenheat_run_task, return_exceptions=True)

def main():
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
