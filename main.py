import asyncio
import logging

from imagestyler import watermark_text
from aiogram.types import BotCommand, InputFile
from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage


API_TOKEN = 'API_TOKEN'


class RegPhoto(StatesGroup):
    waiting_for_in_image = State()
    waiting_for_text = State()
    waiting_for_color = State()
    waiting_for_pos = State()
    # file_image_send = State()


def register_handlers_image(dp: Dispatcher):
    dp.register_message_handler(new_image, commands="new", state="*")
    dp.register_message_handler(get_in_image, state=RegPhoto.waiting_for_in_image, content_types=['photo'])
    dp.register_message_handler(get_text, state=RegPhoto.waiting_for_text)
    dp.register_message_handler(get_color, state=RegPhoto.waiting_for_color)
    dp.register_message_handler(get_pos, state=RegPhoto.waiting_for_pos)
    # dp.register_message_handler(send_image, state=RegPhoto.file_image_send)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")


async def cmd_start(message: types.Message, state: FSMContext):
    """отправляет инструкцию"""
    await state.finish()
    await message.reply(
        "Бот для генерации изображений с помощью AI\n\n"
        "Новое изображение /new\n"
    )

async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено")


async def new_image(message: types.Message):
    """создаёт новое фото"""
    await message.answer("Ожидаю изображение...")
    await RegPhoto.waiting_for_in_image.set()


async def get_in_image(message, state: FSMContext):
    await message.photo[-1].download(f'{message.from_user.id}/in.jpg')
    await RegPhoto.next()
    await message.answer("Ожидаю текст водяного знака...")


async def get_text(message: types.Message, state: FSMContext):
    await state.update_data(mrktext=message.text, user_id=message.from_user.id)
    await RegPhoto.next()
    await message.answer("Ожидаю цвет в формате RGBA без скобок...")


async def get_color(message: types.Message, state: FSMContext):
    await state.update_data(color=message.text)
    await RegPhoto.next()
    await message.answer("Ожидаю позицию в формате 0,0...")


async def get_pos(message: types.Message, state: FSMContext):
    await state.update_data(pos=message.text)
    user_data = await state.get_data()
    await message.answer(f"Текст: {user_data['mrktext']}\n"
                         f"Цвет: {user_data['color']}\n" 
                         f"Поцизия: {user_data['pos']}"
    )  
    watermark_text(user_id=user_data['user_id'],
                   text=user_data['mrktext'],
                   color=tuple(map(int, user_data['color'].split(','))),
                   pos=tuple(map(int, user_data['pos'].split(',')))
    )
    await message.answer_photo(photo=InputFile(f"{message.from_user.id}/out.png"), caption="Готово!")
    await state.finish()


# async def send_image(state: FSMContext):
#     await message.answer("Jopa")
#     await state.finish()


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/new", description="Новое изображение")
    ]
    await bot.set_my_commands(commands)


async def main():
    # логирование
    logging.basicConfig(level=logging.INFO)

    # инициализация бота
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    # рег обработчика
    register_handlers_image(dp)
    register_handlers_common(dp)

    # старт слушанья
    await dp.start_polling()



if __name__ == '__main__':
    asyncio.run(main())