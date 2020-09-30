# Основной Discord клиент для работы -
# by Wokashi RG -
# https://github.com/wokashi-rg -
# Автор який зробив бота для Discord
#-----------------------------------------
# Переписав бота під Telegram
# Koval Yaroslav
# https://github.com/koval01 | https://t.me/koval_yaroslav
# Перша версія 30.07.2020 (Beta 1)
# Друга версія 31.07.2020 (Beta 2)

import logging
from uptime import uptime
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineQuery, \
    InputTextMessageContent, InlineQueryResultArticle, Dice
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import Throttled
from collections import Counter
import sentry_sdk
import requests
import time
import string
import json
import platform
import schedule
import collections
import random
import asyncio
import config
from tokenizer import Tokenizer
from utils.tprint import current_time, log
import predictor

# Заблоковані користувачі (Статичний список)
bannedusers = []

# sentry для отримання помилок в автономному режимі
sentry_sdk.init("https://28a8cabcfd5d408aa493a18a8c667881@sentry.io/5175066")

# рівень логування
logging.basicConfig(level=logging.INFO)

# інніціалізація бота
#bot = Bot(token=str(config.token), parse_mode="HTML")
token_bot = input("Telegram bot token: ")
bot = Bot(token=str(token_bot))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

temperature = config.temperature
tokenizer = Tokenizer()
tokenizer.load_vocab_from_file(config.vocab_file)
channel_deques = {}
custom_emoji_collection = []

# async def set_temperature(value): # Не задействовано
#     try:
#         temperature = float(value)
#     except ValueError:
#         return False
#     if temperature <= 0:
#         return False
#     return True

# Що потрібно відправити при першому знайомстві
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    try:
        await dp.throttle('start', rate=2)
    except Throttled:
        await message.reply('Воу! Не так быстро. (Защита от флуда)')
    else:
        log(str('ID {} использовал команду - "/start"').format(str(message.from_user.id)))
        await message.reply('Привет! Меня создал @koval_yaroslav. Основная моя задача это работа в группах, но я могу отвечать и в привате. Ну, что же пообщаемся?')
        await message.reply('Ver. Beta 2 (310720)\nИнформация о сервере: {} {}\nАптайм: {} секунд'.format(platform.platform(), platform.python_version(), uptime()))
        if message.from_user.id != config.ADMIN:
            await bot.send_message(config.ADMIN,'{}Користувач з ID - {} - використав /start'.format(current_time(), int(message.from_user.id)))

# Команда допомоги
@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    try:
        await dp.throttle('help', rate=2)
    except Throttled:
        await message.reply('Воу! Не так быстро. (Защита от флуда)')
    else:
        log(str('ID {} использовал команду - "/help"').format(str(message.from_user.id)))
        await message.reply("/start - перезагрузка\n/help - инфо\n/dice - могу кинуть кубик")
        if message.from_user.id == config.ADMIN:
            await message.reply('/send - без підпису, /asend - з підписом')

# Гральний кубик
@dp.message_handler(commands=['dice'])
async def help(message: types.Message):
    try:
        await dp.throttle('dice', rate=2)
    except Throttled:
        await message.reply('Воу! Не так быстро. (Защита от флуда)')
    else:
        log(str('ID {} использовал команду - "/dice"').format(str(message.from_user.id)))
        await message.reply_dice('🎲')

@dp.message_handler(content_types=['text'])
async def handle_message_received(message):
    await bot.send_chat_action(int(message.from_user.id), "typing") # Відправляємо користувачі інформацію про те, що бот пише
    data_wait = await message.reply('Думаю...') # Створюємо повідомлення яке будемо редагувати
    data_wait = str(data_wait) # Переводимо в строку
    data_wait = data_wait.replace('{"message_id": ', '') # Обрізаємо початок
    data_wait = data_wait[:data_wait.find(',')] # Обрізаємо кінець
    #-------------------------------------LOG----------------------------------
    log(str('ID {} отправил сообщение боту - "{}"').format(int(message.from_user.id), str(message.text))) # ЛОг в консоль
    #--------------------------------------------------------------------------
    await bot.send_chat_action(int(message.from_user.id), "typing") # Відправляємо користувачі інформацію про те, що бот пише
    input_messages = str(message.text) # Створюємо констатну для передачі тектсу користувача
    input_tensor = tokenizer.encode_input(input_messages, message.from_user.id) # Передаємо текст і ідентифікатор користувача токенізатору
    #--------------------------------------------------------------------------
    await bot.send_chat_action(int(message.from_user.id), "typing") # Відправляємо користувачі інформацію про те, що бот пише
    output_tensor = predictor.decode_sequence(input_tensor, temperature) # Тензор
    await bot.send_chat_action(int(message.from_user.id), "typing") # Відправляємо користувачі інформацію про те, що бот пише
    output_message, token_count = tokenizer.decode_output(input_messages, output_tensor) # Відповідь бота, оброблене повідомлення
    if config.use_delay:
        await bot.send_chat_action(int(message.from_user.id), "typing") # Відправляємо користувачі інформацію про те, що бот пише
        await asyncio.sleep(random.uniform(0.1, 0.2)*token_count) # Симуляцію набору тектса, генерується випадкове число від 0.1 до 0.2 і множить на кількість токенів
    if output_message:
        await bot.edit_message_text(
            text=str(output_message[:2000]),
            chat_id=int(message.from_user.id),
            message_id=int(data_wait),
        ) # Замінюємо повідомлення "Думаю..." на кінцевий результат
        log(str('ID {} получил ответ - "{}"').format(str(message.from_user.id), str(output_message[:2000]))) # Надсилаємо інформацію в консоль\термінал\шелл
        if message.from_user.id != config.ADMIN:
            await bot.send_message(config.ADMIN, str('{}ID {} отправил сообщение "{}" и получил ответ "{}"').format(
                current_time(), 
                str(message.from_user.id), 
                str(message.text), 
                str(output_message[:2000]
                ))) # Відправляємо інформацію для адміністратора
    

if __name__ == '__main__':
    #dp.loop.create_task(handle_message_received(10))
    # Повідомлення про успішний запуск
    log('Бот запущен.')
    #---------------------------------------------
    executor.start_polling(dp, skip_updates=False)
