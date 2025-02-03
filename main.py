# from utils.cfg import cfg_db
# if __name__ == '__main__':
# print(cfg_db.__dict__)

# main.py
import asyncio

from utils.init_app import init_app
from homeworkbot import bot


async def main():
    await asyncio.gather(
        bot.infinity_polling(request_timeout=90)
    )


if __name__ == '__main__':
    init_app()
    asyncio.run(main())
