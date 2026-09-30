import argparse
import asyncio
import logging

from greenheat import GreenHeatClient
from greenheat.models import GreenHeatMessage

logger = logging.getLogger(__name__)


async def on_message(message: GreenHeatMessage):
    logger.debug(f"greenheat event: {message.to_dict()}")


async def run(channel: str):
    async with GreenHeatClient(channel, on_message) as client:
        logger.info(f"listening to {client.channel}, ctrl+c to stop")
        await asyncio.Event().wait()

## Example if you have multiple tasks to run side by side
# async def run(channel: str):
#     client = GreenHeatClient(channel, on_message)
#     greenheat_run_task = asyncio.create_task(client.run())
#     try:
#         tasks = asyncio.gather(greenheat_run_task)
#         await tasks
#     finally:
#         for t in (greenheat_run_task,):
#             t.cancel()
#         await asyncio.gather(greenheat_run_task, return_exceptions=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", required=True)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(levelname)s - [%(name)s] %(message)s",
    )
    logging.getLogger("websockets").setLevel(logging.INFO)

    try:
        asyncio.run(run(args.channel))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
