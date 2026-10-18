import logging
import asyncio 

from aiogram import Dispatcher

from create_bot import bot
from database.models import async_main

from handlers.groups import (group_admin_router,
                             group_member_router, group_profile_router)

from handlers.interface import (infc_admin_router,
                                infc_profile_router, infc_member_router)

async def main():
    await async_main()
    dp = Dispatcher()

    dp.include_routers(group_member_router, group_admin_router,
                       group_profile_router,infc_admin_router,
                       infc_profile_router, infc_member_router)

    await dp.start_polling(bot)

if __name__ == '__main__': 
    logging.basicConfig(level=logging.INFO) 
    try: 
        asyncio.run(main()) 
    except KeyboardInterrupt: 
        print('exit')