import random
import logging

import trio
import triogram


BASE_LOCATION = "https://meet.jit.si"
SLUG_LENGTH = 4


def configure_logging():
    logger = logging.getLogger("triogram")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    logger.addHandler(handler)


def generate_slugs(filename, length):
    with open(filename) as file:
        words = [line.strip() for line in file]

    while True:
        yield "".join(random.sample(words, length))


def meet_command(update):
    try:
        return update["message"]["text"].startswith("/meet")
    except KeyError:
        return False


async def meet_handler(bot, slugs):
    async with bot.sub(meet_command) as updates:
        async for update in updates:
            await bot.api.send_message(
                params={
                    "chat_id": update["message"]["chat"]["id"],
                    "text": f"{BASE_LOCATION}/{next(slugs)}",
                }
            )


async def main():
    bot = triogram.make_bot()
    configure_logging()
    slugs = generate_slugs("emojis.txt", SLUG_LENGTH)

    async with trio.open_nursery() as nursery:
        nursery.start_soon(bot)
        nursery.start_soon(meet_handler, bot, slugs)


if __name__ == "__main__":
    trio.run(main)
