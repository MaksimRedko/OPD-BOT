import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from db.database import init_db

from scr.bot.config import config
from scr.bot.handlers.main_handler import router
from scr.bot.handlers.admin_handler import admin_router
from scr.bot.handlers.user_handler import user_router


# Создаем класс-обработчик для добавления информации о нажатых кнопках
class ButtonClickHandler(logging.Handler):
    def emit(self, record):
        # Передаем информацию о нажатых кнопках в методе emit
        button_info = getattr(record, 'button_info', None)
        if button_info:
            self.format(record)
            print(record.msg)


async def start():
    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(admin_router)
    dp.include_router(router)
    dp.include_router(user_router)

    await bot.delete_webhook(drop_pending_updates=True)

    # Создаем логгер и добавляем к нему наш обработчик
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(ButtonClickHandler())

    # Настройка форматирования сообщений лога
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    init_db()
    asyncio.run(start())
