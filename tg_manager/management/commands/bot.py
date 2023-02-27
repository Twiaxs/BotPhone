import requests
import os
import logging
from dotenv import load_dotenv
from django.conf import settings
from django.core.management.base import BaseCommand
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import start_webhook
from aiogram.dispatcher import Dispatcher

load_dotenv()

#logging
logging.basicConfig(level=logging.INFO,
                    filename='log/bot.log',
                    filemode='a',
                    format='%(asctime)s.%(msecs)d %(levelname)s %(message)s',
                    datefmt='%H:%M:%S')
logging.info('Starting webserver...')


bot = Bot(token=os.environ.get('TELEGRAM_BOT_API_KEY'))
dp = Dispatcher(bot, storage=MemoryStorage())

#create webhook
async def on_startup(dp):
    print('onstartup')
    await bot.set_webhook(settings.WEBHOOK_URL, drop_pending_updates=True)

#del webhook
async def on_shutdown(dp):
    print('onshutdown')
    await bot.delete_webhook()
    
#MSF state
class Test(StatesGroup):
    command_phone = State()

#running bot
class Command(BaseCommand):
    #command start
    async def command_start(message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
        keyboard.add(button_phone)
        await message.reply("Привет, а дай номер", reply_markup=keyboard)
        await Test.next()
        
    #get and post phone number
    async def get_phone(message: types.Message, state: FSMContext):
            await message.answer(f"Спасибо, ваш номер сохранен", reply_markup=types.ReplyKeyboardRemove())
            data = {
                 "phone":message.contact.phone_number,
                 "login":message.from_user.username
            }
            requests.post(url=os.environ.get('URL'), json=data)
            await state.finish()

    def handle(self, *args, **options):
        dp.register_message_handler(Command.command_start, commands=['Start'])
        dp.register_message_handler(Command.get_phone, content_types=types.ContentType.CONTACT, state=Test.command_phone)
        start_webhook(
        dispatcher=dp,
        webhook_path=settings.WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=settings.WEBAPP_HOST,
        port=settings.WEBAPP_PORT,
    )