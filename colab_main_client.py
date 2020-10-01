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

# Реліз 01.10.2020

import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineQuery, \
	InputTextMessageContent, InlineQueryResultArticle, Dice
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import Throttled
from tokenizer import Tokenizer
from utils.tprint import current_time, log
from collections import Counter
import sentry_sdk
import schedule
import collections
import random
import asyncio
import config
import predictor

inp_token = input("Telegram bot token: ")
bannedusers = []
sentry_sdk.init("https://28a8cabcfd5d408aa493a18a8c667881@sentry.io/5175066")
logging.basicConfig(level=logging.INFO)
bot = Bot(token=str(inp_token))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
temperature = config.temperature
tokenizer = Tokenizer()
tokenizer.load_vocab_from_file(config.vocab_file)
channel_deques = {}
custom_emoji_collection = []

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
	await message.reply("Напиши мне что-то...")

@dp.message_handler(content_types=['text'])
async def handle_message_received(message):
	try:
		await dp.throttle('start', rate=float(0.5))
	except Throttled:
		await message.reply('Воу! Не так быстро. (Защита от флуда)')
	else:
		await bot.send_chat_action(int(message.from_user.id), "typing")
		data_wait = await message.reply('Думаю...')
		data_wait = str(data_wait)
		data_wait = data_wait.replace('{"message_id": ', '')
		data_wait = data_wait[:data_wait.find(',')]
		log(str('ID {} отправил сообщение боту - "{}"').format(int(message.from_user.id), str(message.text)))
		input_messages = str(message.text)
		input_tensor = tokenizer.encode_input(input_messages, message.from_user.id)
		await bot.send_chat_action(int(message.from_user.id), "typing")
		output_tensor = predictor.decode_sequence(input_tensor, temperature)
		output_message, token_count = tokenizer.decode_output(input_messages, output_tensor)
		if config.use_delay:
			await bot.send_chat_action(int(message.from_user.id), "typing")
			await asyncio.sleep(random.uniform(0.1, 0.2)*token_count)
		if output_message:
			await bot.edit_message_text(
				text=str(output_message[:2000]),
				chat_id=int(message.from_user.id),
				message_id=int(data_wait))
			log(str('ID {} получил ответ - "{}"').format(str(message.from_user.id), str(output_message[:2000])))
	
if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=False)
