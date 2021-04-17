import re
import sqlite3
import threading
import time
from threading import Thread
import datetime
import requests
import telebot
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.types import ContentType
from aiogram.utils import executor
import KeyBoards
import messages
from config import TOKEN, PAYMENTS_PROVIDER_TOKEN, TIME_MACHINE_IMAGE_URL
from messages import MESSAGES
from utils import Register, Change, Pay, AdminPanel, ScheduleUser, Events


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


bot2 = telebot.TeleBot(__name__)
bot2.config['api_key'] = TOKEN
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

PRICE100 = types.LabeledPrice(label='Поддержка разработчиков 100 Рублей', amount=10000)
PRICE250 = types.LabeledPrice(label='Поддержка разработчиков 250 Рублей', amount=25000)
PRICE500 = types.LabeledPrice(label='Поддержка разработчиков 500 Рублей', amount=50000)
PRICE1000 = types.LabeledPrice(label='Поддержка разработчиков 1000 Рублей', amount=100000)

incoming_events = {}


@dp.message_handler(state=Events.EVENTS_USER_0)
async def process_command0(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    if switch_text == 'меню':
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()

    else:
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Events.all()[1])
        incoming_events[message.from_user.id] = message.text
        await message.reply("Мероприятие успешно добавлено!\nПоставьте таймер:"
                            , reply_markup=KeyBoards.time_kb)


@dp.message_handler(state=Events.EVENTS_USER_1)
async def process_command1(message: types.Message):
    global timing
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    if switch_text == 'меню':
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
    else:
        m = {'1 час': 60 * 60, "2 часа": 60 * 60 * 2, "6 часов": 60 * 60 * 6, "12 часов": 60 * 60 * 12,
             "24 часа": 60 * 60 * 24,
             "2 дня": 60 * 60 * 48, "Неделя": 60 * 60 * 24 * 7}
        if m[message.text]:
            conn = sqlite3.connect('db.db')
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO times(`chat_id`, `event1`, `time`, `30min`, `5min`) values ({message.from_user.id}, '{incoming_events[message.from_user.id]}', {round(time.time() + m[message.text])}, {1}, {1})")
            incoming_events.pop(message.from_user.id)
            conn.commit()
            conn.close()

            is_succeed = False
            conn = sqlite3.connect('db.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT user_id FROM admins")
            result_set = cursor.fetchall()
            cursor.close()
            for item in result_set:
                if item[0] == message.from_user.id:
                    is_succeed = True
            if is_succeed:
                await message.reply('Успешно! ✨'
                                    , reply=False, reply_markup=KeyBoards.menu_admin_kb)
                conn.commit()
                conn.close()
                state = dp.current_state(user=message.from_user.id)
                await state.reset_state()
            else:
                await message.reply('Успешно! ✨'
                                    , reply=False, reply_markup=KeyBoards.menu_user_kb)
                conn.commit()
                conn.close()
                state = dp.current_state(user=message.from_user.id)
                await state.reset_state()


@dp.message_handler(state=AdminPanel.ADMIN_0)
async def process_admin_command2(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")

    if switch_text == 'меню':
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()

    elif switch_text == 'отправить рассылку':
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(AdminPanel.all()[1])
        await message.reply("Введите сообщение для рассылки"
                            ", чтобы вернуться - меню ✨", reply_markup=KeyBoards.return_keyboard)
    elif switch_text == 'отправить рассылку всем пользователям':
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(AdminPanel.all()[7])
        await message.reply("Введите сообщение для рассылки"
                            ", чтобы вернуться - меню ✨", reply_markup=KeyBoards.return_keyboard)


@dp.message_handler(state=AdminPanel.ADMIN_7)
async def process_admin_command1(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    if switch_text == 'меню':
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
    else:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE admins SET last_content = '{message.text}' WHERE user_id = '{message.from_user.id}'")
        conn.commit()
        conn.close()
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(AdminPanel.all()[8])
        await message.reply("Выберите таймер:", reply_markup=KeyBoards.time_kb)


@dp.message_handler(state=AdminPanel.ADMIN_8)
async def process_admin_command4(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    if switch_text == 'меню':
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
    else:
        m = {'1 час': 60 * 60, "2 часа": 60 * 60 * 2, "6 часов": 60 * 60 * 6, "12 часов": 60 * 60 * 12,
             "24 часа": 60 * 60 * 24,
             "2 дня": 60 * 60 * 48, "Неделя": 60 * 60 * 24 * 7}
        if m[message.text]:
            conn = sqlite3.connect('db.db')
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE admins SET `time` = '{round(time.time() + m[message.text])}' WHERE user_id = '{message.from_user.id}'")
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.set_state(AdminPanel.all()[9])
            await message.reply('Вы точно хотите отправить рассылку?', reply=False, reply_markup=KeyBoards.
                                yes_or_no_keyboard)


@dp.message_handler(state=AdminPanel.ADMIN_9)
async def process_admin_command1(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    if switch_text == 'меню':
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
    elif switch_text == 'да':
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT chat_id FROM users")
        id_users = cursor.fetchall()
        cursor.close()
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT last_content FROM admins WHERE user_id = '{message.from_user.id}'")
        content = cursor.fetchall()
        cursor.execute(f"SELECT `real_name` FROM users WHERE chat_id = '{message.from_user.id}'")
        name = cursor.fetchall()
        cursor.execute(f"SELECT `time` FROM admins WHERE user_id = '{message.from_user.id}'")
        time2 = cursor.fetchall()
        cursor.close()
        for user in id_users:
            try:
                a = f'Рассылка от пользователя: {name[0][0]}\n' + f'{content[0][0]}'
                conn = sqlite3.connect('db.db')
                cursor = conn.cursor()
                cursor.execute(
                    f"INSERT INTO mail(`chat_id`, `event1`, `time`, `30min`, `5min`) values ({user[0]}, "
                    f"'{content[0][0]}', {time2[0][0]}, {1}, {1})")

                conn.commit()
                conn.close()
                await dp.bot.send_message(user[0], a)
            except:
                pass

        await dp.bot.send_message(message.from_user.id,
                                  f'Ваша рассылка: <b>{content[0][0]}</b>\nУспешно отправлена всем!'
                                  , parse_mode='HTML')
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(AdminPanel.all()[3])
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Успешно! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Успешно! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()

    elif switch_text == 'изменить':
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(AdminPanel.all()[0])
        await message.reply("Выберите действие ✨", reply_markup=KeyBoards.admin_panel)


@dp.message_handler(state=AdminPanel.ADMIN_1)
async def process_admin_command1(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    if switch_text == 'меню':
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
    else:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE admins SET last_content = '{message.text}' WHERE user_id = '{message.from_user.id}'")
        conn.commit()
        conn.close()
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(AdminPanel.all()[2])
        await message.reply("Кому отправить данную расслыку? Выберите инстиут", reply_markup=KeyBoards.institute_kb)


@dp.message_handler(state=AdminPanel.ADMIN_2)
async def process_admin_command4(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    if switch_text == 'меню':
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
    else:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE admins SET inst = '{message.text}' WHERE user_id = '{message.from_user.id}'")
        conn.commit()
        conn.close()
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(AdminPanel.all()[3])
        await message.reply("Выберите курс", reply_markup=KeyBoards.course_kb)


@dp.message_handler(state=AdminPanel.ADMIN_3)
async def process_admin_command4(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    if switch_text == 'меню':
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
    else:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE admins SET course = '{message.text}' WHERE user_id = '{message.from_user.id}'")
        conn.commit()
        conn.close()
        state = dp.current_state(user=message.from_user.id)
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id, inst, course FROM admins")
        result_set = cursor.fetchall()
        for i in result_set:
            if i[0] == message.from_user.id:
                # ИКИТ
                if i[1] == "ИКИТ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.ikit_kb)
                elif i[1] == "ИКИТ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.ikit_kb)
                elif i[1] == "ИКИТ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.ikit_kb)
                elif i[1] == "ИКИТ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.ikit_kb)
                elif i[1] == "ИКИТ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.ikit_kb)
                # ИУБП
                elif i[1] == "ИУБП" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИУБП" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИУБП" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИУБП" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИУБП" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИФБИБТ
                elif i[1] == "ИФБиБТ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФБиБТ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФБиБТ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФБиБТ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФБиБТ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИФИЯК
                elif i[1] == "ИФиЯК" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФиЯК" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФиЯК" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФиЯК" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФиЯК" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ВУЦ
                elif i[1] == "ВУЦ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ВУЦ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ВУЦ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ВУЦ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ВУЦ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ГИ
                elif i[1] == "ГИ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ГИ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ГИ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ГИ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ГИ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИСИ
                elif i[1] == "ИСИ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИСИ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИСИ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИСИ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИСИ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИНИГ
                elif i[1] == "ИНиГ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИНиГ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИНиГ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИНиГ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИНиГ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИАИД
                elif i[1] == "ИАиД" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИАиД" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИАиД" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИАиД" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИАиД" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИГДГиГ
                elif i[1] == "ИГДГиГ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГДГиГ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГДГиГ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГДГиГ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГДГиГ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИИФиРЭ
                elif i[1] == "ИИФиРЭ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИИФиРЭ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИИФиРЭ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИИФиРЭ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИИФиРЭ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИМИФИ
                elif i[1] == "ИМиФИ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИМиФИ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИМиФИ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИМиФИ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИМиФИ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИППС
                elif i[1] == "ИППС" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИППС" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИППС" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИППС" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИППС" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИФКСИТ
                elif i[1] == "ИФКСиТ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФКСиТ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФКСиТ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФКСиТ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФКСиТ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИЦМИМ
                elif i[1] == "ИЦМиМ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЦМиМ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЦМиМ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЦМиМ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЦМиМ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИЭИГ
                elif i[1] == "ИЭиГ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭиГ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭиГ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭиГ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭиГ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИГ
                elif i[1] == "ИГ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИТИСУ
                elif i[1] == "ИТиСУ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИТиСУ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИТиСУ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИТиСУ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИТиСУ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИЭУИФ
                elif i[1] == "ИЭУиФ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭУиФ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭУиФ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭУиФ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭУиФ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ПИ
                elif i[1] == "ПИ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ПИ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ПИ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ПИ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ПИ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ЮИ
                elif i[1] == "ЮИ" and i[2] == "1 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ЮИ" and i[2] == "2 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ЮИ" and i[2] == "3 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ЮИ" and i[2] == "4 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ЮИ" and i[2] == "5 курс":
                    await state.set_state(AdminPanel.all()[4])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
        conn.commit()
        conn.close()


@dp.message_handler(state=AdminPanel.ADMIN_4)
async def process_admin_command4(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    if switch_text == 'меню':
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
    else:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE admins SET `group` = '{message.text}' WHERE user_id = '{message.from_user.id}'")
        conn.commit()
        conn.close()
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(AdminPanel.all()[5])
        await message.reply('Выберите таймер:', reply=False, reply_markup=KeyBoards.time_kb)


@dp.message_handler(state=AdminPanel.ADMIN_5)
async def process_admin_command4(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    if switch_text == 'меню':
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
    else:
        m = {'1 час': 60 * 60, "2 часа": 60 * 60 * 2, "6 часов": 60 * 60 * 6, "12 часов": 60 * 60 * 12,
             "24 часа": 60 * 60 * 24,
             "2 дня": 60 * 60 * 48, "Неделя": 60 * 60 * 24 * 7}
        if m[message.text]:
            conn = sqlite3.connect('db.db')
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE admins SET `time` = '{round(time.time() + m[message.text])}' WHERE user_id = '{message.from_user.id}'")
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.set_state(AdminPanel.all()[6])
            await message.reply('Вы точно хотите отправить рассылку?', reply=False, reply_markup=KeyBoards.
                                yes_or_no_keyboard)


@dp.message_handler(state=AdminPanel.ADMIN_6)
async def process_admin_command1(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    if switch_text == 'меню':
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
    elif switch_text == 'да':
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT chat_id FROM users")
        id_users = cursor.fetchall()
        cursor.close()
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT last_content FROM admins WHERE user_id = '{message.from_user.id}'")
        content = cursor.fetchall()
        cursor.execute(f"SELECT `group` FROM admins WHERE user_id = '{message.from_user.id}'")
        group = cursor.fetchall()
        cursor.execute(f"SELECT `real_name` FROM users WHERE chat_id = '{message.from_user.id}'")
        name = cursor.fetchall()
        cursor.execute(f"SELECT `time` FROM admins WHERE user_id = '{message.from_user.id}'")
        time2 = cursor.fetchall()
        cursor.close()
        for user in id_users:
            conn = sqlite3.connect('db.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT `user_group` FROM users WHERE chat_id = '{user[0]}'")
            group_users = cursor.fetchall()
            cursor.close()
            if group_users == group:
                try:
                    a = f'Рассылка от пользователя: {name[0][0]}\n' + f'{content[0][0]}'
                    conn = sqlite3.connect('db.db')
                    cursor = conn.cursor()
                    cursor.execute(
                        f"INSERT INTO mail(`chat_id`, `event1`, `time`, `30min`, `5min`) values ({user[0]}, '{content[0][0]}', {time2[0][0]}, {1}, {1})")

                    conn.commit()
                    conn.close()
                    await dp.bot.send_message(user[0], a)
                except:
                    pass
        await dp.bot.send_message(message.from_user.id,
                                  f'Ваша рассылка: <b>{content[0][0]}</b>\nУспешно отправлена группе '
                                  f'<b>{group[0][0]}</b>', parse_mode='HTML')
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(AdminPanel.all()[3])
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Успешно! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Успешно! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()

    elif switch_text == 'изменить':
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(AdminPanel.all()[0])
        await message.reply("Выберите действие ✨", reply_markup=KeyBoards.admin_panel)


@dp.message_handler(state=Pay.PAY_DISTRIBUTOR)
async def process_buy_command0(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    if message.text == 'Меню':
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
    elif message.text == 'Узнать команду разработчиков':
        await message.reply('✨ Разработчики телеграм-бота:\n 1. Шульц Илья\n 2.Присяжнюк Кирилл\n 3.Степанцов Антон',
                            reply_markup=KeyBoards.developer_support_kb)
    elif message.text == 'Поддержать разработку телеграмм-бота':
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Pay.all()[1])
        await message.reply("Спасибо, что решили поддержать нашего телеграмм-бота! 🔥"
                            , reply_markup=KeyBoards.developer_support_kb2)


@dp.message_handler(state=Pay.PAY_DISTRIBUTOR2)
async def process_buy_command01(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    if message.text == 'Меню':
        state = dp.current_state(user=message.from_user.id)
        await state.reset_state()
        await message.reply("Вы в меню ✨", reply_markup=KeyBoards.menu_admin_kb)
    elif switch_text == "поддержать разработчиков 100 рублей":
        if PAYMENTS_PROVIDER_TOKEN.split(':')[1] == 'TEST':
            await bot.send_message(message.chat.id, MESSAGES['pre_buy_demo_alert'])
        await bot.send_invoice(message.chat.id,
                               title=MESSAGES['tm_title'],
                               description=MESSAGES['tm_description'],
                               provider_token=PAYMENTS_PROVIDER_TOKEN,
                               currency='rub',
                               photo_url=TIME_MACHINE_IMAGE_URL,
                               photo_height=512,  # !=0/None, иначе изображение не покажется
                               photo_width=512,
                               photo_size=512,
                               is_flexible=False,  # True если конечная цена зависит от способа доставки
                               prices=[PRICE100],
                               start_parameter='developer-support',
                               payload='some-invoice-payload-for-our-internal-use'
                               )
    elif switch_text == "поддержать разработчиков 250 рублей":
        if PAYMENTS_PROVIDER_TOKEN.split(':')[1] == 'TEST':
            await bot.send_message(message.chat.id, MESSAGES['pre_buy_demo_alert'])
        await bot.send_invoice(message.chat.id,
                               title=MESSAGES['tm_title'],
                               description=MESSAGES['tm_description'],
                               provider_token=PAYMENTS_PROVIDER_TOKEN,
                               currency='rub',
                               photo_url=TIME_MACHINE_IMAGE_URL,
                               photo_height=512,  # !=0/None, иначе изображение не покажется
                               photo_width=512,
                               photo_size=512,
                               is_flexible=False,  # True если конечная цена зависит от способа доставки
                               prices=[PRICE250],
                               start_parameter='developer-support',
                               payload='some-invoice-payload-for-our-internal-use'
                               )
    elif switch_text == "поддержать разработчиков 500 рублей":
        if PAYMENTS_PROVIDER_TOKEN.split(':')[1] == 'TEST':
            await bot.send_message(message.chat.id, MESSAGES['pre_buy_demo_alert'])
        await bot.send_invoice(message.chat.id,
                               title=MESSAGES['tm_title'],
                               description=MESSAGES['tm_description'],
                               provider_token=PAYMENTS_PROVIDER_TOKEN,
                               currency='rub',
                               photo_url=TIME_MACHINE_IMAGE_URL,
                               photo_height=512,  # !=0/None, иначе изображение не покажется
                               photo_width=512,
                               photo_size=512,
                               is_flexible=False,  # True если конечная цена зависит от способа доставки
                               prices=[PRICE500],
                               start_parameter='developer-support',
                               payload='some-invoice-payload-for-our-internal-use'
                               )
    elif switch_text == "поддержать разработчиков 1000 рублей":
        if PAYMENTS_PROVIDER_TOKEN.split(':')[1] == 'TEST':
            await bot.send_message(message.chat.id, MESSAGES['pre_buy_demo_alert'])
        await bot.send_invoice(message.chat.id,
                               title=MESSAGES['tm_title'],
                               description=MESSAGES['tm_description'],
                               provider_token=PAYMENTS_PROVIDER_TOKEN,
                               currency='rub',
                               photo_url=TIME_MACHINE_IMAGE_URL,
                               photo_height=512,  # !=0/None, иначе изображение не покажется
                               photo_width=512,
                               photo_size=512,
                               is_flexible=False,  # True если конечная цена зависит от способа доставки
                               prices=[PRICE1000],
                               start_parameter='developer-support',
                               payload='some-invoice-payload-for-our-internal-use'
                               )


@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    print('successful_payment:')
    pmnt = message.successful_payment.to_python()
    for key, val in pmnt.items():
        print(f'{key} = {val}')

    await bot.send_message(
        message.chat.id,
        MESSAGES['successful_payment'].format(
            total_amount=message.successful_payment.total_amount // 100,
            currency=message.successful_payment.currency
        )
    )
    state = dp.current_state(user=message.from_user.id)
    await state.reset_state()
    await message.reply("Вы в меню ✨", reply_markup=KeyBoards.menu_admin_kb)


@dp.message_handler(state=Change.CHANGE_0)
async def name_change(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    else:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET real_name = '{message.text}' WHERE chat_id = '{message.from_user.id}'")
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()


@dp.message_handler(state=Register.REGISTER_0)
async def register_1(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    else:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET real_name = '{message.text}' WHERE chat_id = '{message.from_user.id}'")
        conn.commit()
        conn.close()
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[1])
        await message.reply(messages.institute_message, reply=False, reply_markup=KeyBoards.institute_kb)


@dp.message_handler(state=Register.REGISTER_1)
async def register_2(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    else:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET school = '{message.text}' WHERE chat_id = '{message.from_user.id}'")
        conn.commit()
        conn.close()
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[2])
        await message.reply(messages.course_message, reply=False, reply_markup=KeyBoards.course_kb)


@dp.message_handler(state=Register.REGISTER_2)
async def register_2(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    else:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET course = '{message.text}' WHERE chat_id = '{message.from_user.id}'")
        conn.commit()
        conn.close()
        state = dp.current_state(user=message.from_user.id)
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT chat_id, school, course FROM users")
        result_set = cursor.fetchall()
        for i in result_set:
            if i[0] == message.from_user.id:
                # ИКИТ
                if i[1] == "ИКИТ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.ikit_kb)
                elif i[1] == "ИКИТ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.ikit_kb)
                elif i[1] == "ИКИТ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.ikit_kb)
                elif i[1] == "ИКИТ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.ikit_kb)
                elif i[1] == "ИКИТ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.ikit_kb)
                # ИУБП
                elif i[1] == "ИУБП" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИУБП" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИУБП" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИУБП" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИУБП" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИФБИБТ
                elif i[1] == "ИФБиБТ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФБиБТ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФБиБТ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФБиБТ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФБиБТ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИФИЯК
                elif i[1] == "ИФиЯК" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФиЯК" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФиЯК" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФиЯК" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФиЯК" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ВУЦ
                elif i[1] == "ВУЦ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ВУЦ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ВУЦ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ВУЦ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ВУЦ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ГИ
                elif i[1] == "ГИ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ГИ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ГИ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ГИ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ГИ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИСИ
                elif i[1] == "ИСИ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИСИ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИСИ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИСИ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИСИ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИНИГ
                elif i[1] == "ИНиГ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИНиГ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИНиГ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИНиГ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИНиГ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИАИД
                elif i[1] == "ИАиД" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИАиД" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИАиД" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИАиД" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИАиД" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИГДГиГ
                elif i[1] == "ИГДГиГ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГДГиГ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГДГиГ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГДГиГ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГДГиГ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИИФиРЭ
                elif i[1] == "ИИФиРЭ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИИФиРЭ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИИФиРЭ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИИФиРЭ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИИФиРЭ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИМИФИ
                elif i[1] == "ИМиФИ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИМиФИ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИМиФИ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИМиФИ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИМиФИ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИППС
                elif i[1] == "ИППС" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИППС" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИППС" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИППС" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИППС" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИФКСИТ
                elif i[1] == "ИФКСиТ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФКСиТ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФКСиТ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФКСиТ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФКСиТ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИЦМИМ
                elif i[1] == "ИЦМиМ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЦМиМ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЦМиМ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЦМиМ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЦМиМ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИЭИГ
                elif i[1] == "ИЭиГ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭиГ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭиГ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭиГ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭиГ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИГ
                elif i[1] == "ИГ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИТИСУ
                elif i[1] == "ИТиСУ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИТиСУ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИТиСУ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИТиСУ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИТиСУ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИЭУИФ
                elif i[1] == "ИЭУиФ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭУиФ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭУиФ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭУиФ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭУиФ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ПИ
                elif i[1] == "ПИ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ПИ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ПИ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ПИ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ПИ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ЮИ
                elif i[1] == "ЮИ" and i[2] == "1 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ЮИ" and i[2] == "2 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ЮИ" and i[2] == "3 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ЮИ" and i[2] == "4 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ЮИ" and i[2] == "5 курс":
                    await state.set_state(Register.all()[3])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)

        conn.commit()
        conn.close()


@dp.message_handler(state=Register.REGISTER_3)
async def register_3(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    else:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET user_group = '{message.text}' WHERE chat_id = '{message.from_user.id}'")
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        is_succeed = False
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply(messages.end_of_registration_message
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply(messages.end_of_registration_message
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()


@dp.message_handler(state=ScheduleUser.SCHEDULE_USER_0)
async def schedule_0(msg: types.Message):
    switch_text = msg.text.lower()
    if msg.text == '/start':
        if msg.from_user.username != None:
            await msg.reply(f'Welcome to StudentHelperBot, {msg.from_user.username}🔥\n'
                            '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                            '\n - Поставить напоминания 🍻'
                            '\n - Подписаться на рассылки ✉'
                            '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                            ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await msg.reply(f'Welcome to StudentHelperBot! 🔥\n'
                            '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                            '\n - Поставить напоминания 🍻'
                            '\n - Подписаться на рассылки ✉'
                            '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                            ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=msg.from_user.id)
        await state.set_state(Register.all()[0])
        await msg.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    else:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO user_table(chat_id) values ({msg.from_user.id})")
        cursor.execute(f"UPDATE user_table SET school = '{msg.text}' WHERE chat_id = '{msg.from_user.id}'")
        conn.commit()
        conn.close()
        state = dp.current_state(user=msg.from_user.id)
        await state.set_state(ScheduleUser.all()[1])
        await msg.reply('Выберите курс 👇', reply=False, reply_markup=KeyBoards.course_kb)


@dp.message_handler(state=ScheduleUser.SCHEDULE_USER_1)
async def schedule_0(message: types.Message):
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    else:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE user_table SET course = '{message.text}' WHERE chat_id = '{message.from_user.id}'")
        conn.commit()
        conn.close()
        state = dp.current_state(user=message.from_user.id)
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT chat_id, school, course FROM user_table")
        result_set = cursor.fetchall()
        for i in result_set:
            if i[0] == message.from_user.id:
                # ИКИТ
                if i[1] == "ИКИТ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.ikit_kb)
                elif i[1] == "ИКИТ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.ikit_kb)
                elif i[1] == "ИКИТ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.ikit_kb)
                elif i[1] == "ИКИТ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.ikit_kb)
                elif i[1] == "ИКИТ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.ikit_kb)
                # ИУБП
                elif i[1] == "ИУБП" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИУБП" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИУБП" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИУБП" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИУБП" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИФБИБТ
                elif i[1] == "ИФБиБТ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФБиБТ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФБиБТ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФБиБТ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФБиБТ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИФИЯК
                elif i[1] == "ИФиЯК" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФиЯК" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФиЯК" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФиЯК" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФиЯК" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ВУЦ
                elif i[1] == "ВУЦ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ВУЦ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ВУЦ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ВУЦ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ВУЦ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ГИ
                elif i[1] == "ГИ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ГИ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ГИ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ГИ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ГИ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИСИ
                elif i[1] == "ИСИ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИСИ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИСИ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИСИ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИСИ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИНИГ
                elif i[1] == "ИНиГ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИНиГ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИНиГ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИНиГ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИНиГ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИАИД
                elif i[1] == "ИАиД" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИАиД" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИАиД" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИАиД" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИАиД" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИГДГиГ
                elif i[1] == "ИГДГиГ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГДГиГ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГДГиГ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГДГиГ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГДГиГ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИИФиРЭ
                elif i[1] == "ИИФиРЭ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИИФиРЭ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИИФиРЭ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИИФиРЭ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИИФиРЭ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИМИФИ
                elif i[1] == "ИМиФИ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИМиФИ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИМиФИ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИМиФИ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИМиФИ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИППС
                elif i[1] == "ИППС" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИППС" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИППС" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИППС" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИППС" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИФКСИТ
                elif i[1] == "ИФКСиТ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФКСиТ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФКСиТ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФКСиТ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИФКСиТ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИЦМИМ
                elif i[1] == "ИЦМиМ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЦМиМ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЦМиМ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЦМиМ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЦМиМ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИЭИГ
                elif i[1] == "ИЭиГ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭиГ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭиГ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭиГ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭиГ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИГ
                elif i[1] == "ИГ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИГ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИТИСУ
                elif i[1] == "ИТиСУ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИТиСУ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИТиСУ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИТиСУ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИТиСУ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ИЭУИФ
                elif i[1] == "ИЭУиФ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭУиФ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭУиФ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭУиФ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ИЭУиФ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ПИ
                elif i[1] == "ПИ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ПИ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ПИ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ПИ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ПИ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                # ЮИ
                elif i[1] == "ЮИ" and i[2] == "1 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ЮИ" and i[2] == "2 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ЮИ" and i[2] == "3 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ЮИ" and i[2] == "4 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
                elif i[1] == "ЮИ" and i[2] == "5 курс":
                    await state.set_state(ScheduleUser.all()[2])
                    await message.reply(messages.group_message, reply=False, reply_markup=KeyBoards.gi_kb)
        conn.commit()
        conn.close()


@dp.message_handler(state=ScheduleUser.SCHEDULE_USER_2)
async def register_3(message: types.Message):
    global group
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    else:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE user_table SET user_group = '{message.text}' WHERE chat_id = '{message.from_user.id}'")
        conn.commit()
        conn.close()
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(ScheduleUser.all()[3])
        await message.reply('Выберите день недели', reply=False, reply_markup=KeyBoards.day_of_the_week_kb)


@dp.message_handler(state=ScheduleUser.SCHEDULE_USER_3)
async def register_3(message: types.Message):
    global group
    switch_text = message.text.lower()
    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)

    elif switch_text == "регистрация":
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Register.all()[0])
        await message.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")
    elif switch_text == 'меню':
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == message.from_user.id:
                is_succeed = True
        if is_succeed:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
        else:
            await message.reply('Вы в меню! ✨'
                                , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=message.from_user.id)
            await state.reset_state()
    else:
        if switch_text == 'понедельник':
            timetable_message = ""
            current_week = "0"
            url = 'https://edu.sfu-kras.ru/timetable'
            response = requests.get(url).text
            match = re.search(r'Идёт\s\w{8}\sнеделя', response)
            if match:
                current_week = "1"
            else:
                current_week = "2"
            conn = sqlite3.connect('db.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT user_group FROM user_table WHERE chat_id = '{message.from_user.id}'")
            result_set1 = cursor.fetchall()
            conn.commit()
            conn.close()
            url = (f'http://edu.sfu-kras.ru/api/timetable/get?target={result_set1[0][0]}')
            response = requests.get(url).json()
            adding = []
            for item in response["timetable"]:
                if item["week"] == current_week:
                    adding.append(
                        [item['day'], item['time'], item['subject'], item['type'], item['teacher'], item['place']])
            flag = 0
            for i in adding:
                if i[0] == '1':
                    if i[2] != '':
                        flag = 1
            if flag == 1:
                if match:
                    timetable_message += "Сейчас идёт <b>нечётная</b> неделя\n"
                else:
                    timetable_message += "Сейчас идёт <b>чётная</b> неделя\n"
                timetable_message += '\n\t\t\t\t\t\t\t\t\t<b>Понедельник</b>\n\t\t~~~~~~~~~~~~~~~~~~~'
                for i in adding:
                    if i[0] == '1':
                        if i[4] == '' and i[5] == '':
                            timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]})\n'
                        else:
                            timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]}) \n{i[4]}\n<b>{i[5]}</b>\n'
            else:
                timetable_message += 'В понедельник пар нет!\n Отличный повод увидеться с друзьями! 🎉'
            await message.reply(timetable_message, parse_mode="HTML")

        if switch_text == 'вторник':
            timetable_message = ""
            current_week = "0"
            url = 'https://edu.sfu-kras.ru/timetable'
            response = requests.get(url).text
            match = re.search(r'Идёт\s\w{8}\sнеделя', response)
            if match:
                current_week = "1"
            else:
                current_week = "2"
            conn = sqlite3.connect('db.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT user_group FROM user_table WHERE chat_id = '{message.from_user.id}'")
            result_set1 = cursor.fetchall()
            conn.commit()
            conn.close()
            url = (f'http://edu.sfu-kras.ru/api/timetable/get?target={result_set1[0][0]}')
            response = requests.get(url).json()
            adding = []
            for item in response["timetable"]:
                if item["week"] == current_week:
                    adding.append(
                        [item['day'], item['time'], item['subject'], item['type'], item['teacher'], item['place']])
            flag = 0
            for i in adding:
                if i[0] == '2':
                    if i[2] != '':
                        flag = 1
            if flag == 1:
                if match:
                    timetable_message += "Сейчас идёт <b>нечётная</b> неделя\n"
                else:
                    timetable_message += "Сейчас идёт <b>чётная</b> неделя\n"
                timetable_message += '\n\t\t\t\t\t\t\t\t\t<b>Вторник</b>\n\t\t~~~~~~~~~~~~~~~~~~~'
                for i in adding:
                    if i[0] == '2':
                        if i[4] == '' and i[5] == '':
                            timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]})\n'
                        else:
                            timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]}) \n{i[4]}\n<b>{i[5]}</b>\n'
            else:
                timetable_message += 'Во вторник пар нет!\n Отличный повод увидеться с друзьями! 🎉'
            await message.reply(timetable_message, parse_mode="HTML")

        if switch_text == 'среда':
            timetable_message = ""
            current_week = "0"
            url = 'https://edu.sfu-kras.ru/timetable'
            response = requests.get(url).text
            match = re.search(r'Идёт\s\w{8}\sнеделя', response)
            if match:
                current_week = "1"
            else:
                current_week = "2"
            conn = sqlite3.connect('db.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT user_group FROM user_table WHERE chat_id = '{message.from_user.id}'")
            result_set1 = cursor.fetchall()
            conn.commit()
            conn.close()
            url = (f'http://edu.sfu-kras.ru/api/timetable/get?target={result_set1[0][0]}')
            response = requests.get(url).json()
            adding = []
            for item in response["timetable"]:
                if item["week"] == current_week:
                    adding.append(
                        [item['day'], item['time'], item['subject'], item['type'], item['teacher'], item['place']])
            flag = 0
            for i in adding:
                if i[0] == '3':
                    if i[2] != '':
                        flag = 1
            if flag == 1:
                if match:
                    timetable_message += "Сейчас идёт <b>нечётная</b> неделя\n"
                else:
                    timetable_message += "Сейчас идёт <b>чётная</b> неделя\n"
                timetable_message += '\n\t\t\t\t\t\t\t\t\t<b>Среда</b>\n\t\t~~~~~~~~~~~~~~~~~~~'
                for i in adding:
                    if i[0] == '3':
                        if i[4] == '' and i[5] == '':
                            timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]})\n'
                        else:
                            timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]}) \n{i[4]}\n<b>{i[5]}</b>\n'
            else:
                timetable_message += 'В среду пар нет!\n Отличный повод увидеться с друзьями! 🎉'
            await message.reply(timetable_message, parse_mode="HTML")

        if switch_text == 'четверг':
            timetable_message = ""
            current_week = "0"
            url = 'https://edu.sfu-kras.ru/timetable'
            response = requests.get(url).text
            match = re.search(r'Идёт\s\w{8}\sнеделя', response)
            if match:
                current_week = "1"
            else:
                current_week = "2"
            conn = sqlite3.connect('db.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT user_group FROM user_table WHERE chat_id = '{message.from_user.id}'")
            result_set1 = cursor.fetchall()
            conn.commit()
            conn.close()
            url = (f'http://edu.sfu-kras.ru/api/timetable/get?target={result_set1[0][0]}')
            response = requests.get(url).json()
            adding = []
            for item in response["timetable"]:
                if item["week"] == current_week:
                    adding.append(
                        [item['day'], item['time'], item['subject'], item['type'], item['teacher'], item['place']])
            flag = 0
            for i in adding:
                if i[0] == '4':
                    if i[2] != '':
                        flag = 1
            if flag == 1:
                if match:
                    timetable_message += "Сейчас идёт <b>нечётная</b> неделя\n"
                else:
                    timetable_message += "Сейчас идёт <b>чётная</b> неделя\n"
                timetable_message += '\n\t\t\t\t\t\t\t\t\t<b>Четверг</b>\n\t\t~~~~~~~~~~~~~~~~~~~'
                for i in adding:
                    if i[0] == '4':
                        if i[4] == '' and i[5] == '':
                            timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]})\n'
                        else:
                            timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]}) \n{i[4]}\n<b>{i[5]}</b>\n'
            else:
                timetable_message += 'В четверг пар нет!\n Отличный повод увидеться с друзьями! 🎉'
            await message.reply(timetable_message, parse_mode="HTML")

        if switch_text == 'пятница':
            timetable_message = ""
            current_week = "0"
            url = 'https://edu.sfu-kras.ru/timetable'
            response = requests.get(url).text
            match = re.search(r'Идёт\s\w{8}\sнеделя', response)
            if match:
                current_week = "1"
            else:
                current_week = "2"
            conn = sqlite3.connect('db.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT user_group FROM user_table WHERE chat_id = '{message.from_user.id}'")
            result_set1 = cursor.fetchall()
            conn.commit()
            conn.close()
            url = (f'http://edu.sfu-kras.ru/api/timetable/get?target={result_set1[0][0]}')
            response = requests.get(url).json()
            adding = []
            for item in response["timetable"]:
                if item["week"] == current_week:
                    adding.append(
                        [item['day'], item['time'], item['subject'], item['type'], item['teacher'], item['place']])
            flag = 0
            for i in adding:
                if i[0] == '5':
                    if i[2] != '':
                        flag = 1
            if flag == 1:
                if match:
                    timetable_message += "Сейчас идёт <b>нечётная</b> неделя\n"
                else:
                    timetable_message += "Сейчас идёт <b>чётная</b> неделя\n"
                timetable_message += '\n\t\t\t\t\t\t\t\t\t<b>Пятница</b>\n\t\t~~~~~~~~~~~~~~~~~~~'
                for i in adding:
                    if i[0] == '5':
                        if i[4] == '' and i[5] == '':
                            timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]})\n'
                        else:
                            timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]}) \n{i[4]}\n<b>{i[5]}</b>\n'
            else:
                timetable_message += 'В пятницу пар нет!\n Отличный повод увидеться с друзьями! 🎉'
            await message.reply(timetable_message, parse_mode="HTML")

        if switch_text == 'суббота':
            timetable_message = ""
            current_week = "0"
            url = 'https://edu.sfu-kras.ru/timetable'
            response = requests.get(url).text
            match = re.search(r'Идёт\s\w{8}\sнеделя', response)
            if match:
                current_week = "1"
            else:
                current_week = "2"
            conn = sqlite3.connect('db.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT user_group FROM user_table WHERE chat_id = '{message.from_user.id}'")
            result_set1 = cursor.fetchall()
            conn.commit()
            conn.close()
            url = (f'http://edu.sfu-kras.ru/api/timetable/get?target={result_set1[0][0]}')
            response = requests.get(url).json()
            adding = []
            for item in response["timetable"]:
                if item["week"] == current_week:
                    adding.append(
                        [item['day'], item['time'], item['subject'], item['type'], item['teacher'], item['place']])
            flag = 0
            for i in adding:
                if i[0] == '6':
                    if i[2] != '':
                        flag = 1
            if flag == 1:
                if match:
                    timetable_message += "Сейчас идёт <b>нечётная</b> неделя\n"
                else:
                    timetable_message += "Сейчас идёт <b>чётная</b> неделя\n"
                timetable_message += '\n\t\t\t\t\t\t\t\t\t<b>Суббота</b>\n\t\t~~~~~~~~~~~~~~~~~~~'
                for i in adding:
                    if i[0] == '6':
                        if i[4] == '' and i[5] == '':
                            timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]})\n'
                        else:
                            timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]}) \n{i[4]}\n<b>{i[5]}</b>\n'
            else:
                timetable_message += 'В субботу пар нет!\n Отличный повод увидеться с друзьями! 🎉'
            await message.reply(timetable_message, parse_mode="HTML")


@dp.message_handler(commands='start')
async def process_start_command(message: types.Message):
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO users(chat_id, name) values ({message.from_user.id}, '{message.from_user.username}')")
    conn.commit()
    conn.close()

    if message.text == '/start':
        if message.from_user.username != None:
            await message.reply(f'Welcome to StudentHelperBot, {message.from_user.username}🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
        else:
            await message.reply(f'Welcome to StudentHelperBot! 🔥\n'
                                '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                                '\n - Поставить напоминания 🍻'
                                '\n - Подписаться на рассылки ✉'
                                '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                                ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)


@dp.message_handler(commands='help')
async def process_start2_command(message: types.Message):
    if message.from_user.username == None:
        await message.reply(f'Welcome to StudentHelperBot! 🔥, {message.from_user.username}.\n'
                            '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                            '\n - Поставить напоминания 🍻'
                            '\n - Подписаться на рассылки ✉'
                            '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                            ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)
    else:
        await message.reply(f'Welcome to StudentHelperBot! 🔥.\n'
                            '\n - Здесь всегда можно узнать актуальное расписание 🎓'
                            '\n - Поставить напоминания 🍻'
                            '\n - Подписаться на рассылки ✉'
                            '\n - У нас есть свои PevCoin\'ы (валюта в разработке) 💵'
                            ' \n  Регистрируемся? ✨', reply_markup=KeyBoards.greet_kb)


@dp.message_handler(state='*', content_types=["text"])
async def handler_message(msg: types.Message):
    global adding
    global group
    switch_text = msg.text.lower()
    if switch_text == "расписание":
        await msg.reply("Выберите день недели", reply_markup=KeyBoards.day_of_the_week_kb)
    elif switch_text == "понедельник":
        timetable_message = ""

        url = 'https://edu.sfu-kras.ru/timetable'
        response = requests.get(url).text
        match = re.search(r'Идёт\s\w{8}\sнеделя', response)
        if match:
            current_week = "1"
        else:
            current_week = "2"
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT chat_id, user_group FROM users")
        result_set = cursor.fetchall()
        cursor.close()
        for i in result_set:
            if i[0] == msg.from_user.id:
                group = i[1]
        url = (f'http://edu.sfu-kras.ru/api/timetable/get?target={group}')
        response = requests.get(url).json()
        adding = []
        for item in response["timetable"]:
            if item["week"] == current_week:
                adding.append(
                    [item['day'], item['time'], item['subject'], item['type'], item['teacher'], item['place']])
        flag = 0
        for i in adding:
            if i[0] == '1':
                if i[2] != '':
                    flag = 1
        if flag == 1:
            if match:
                timetable_message += "Сейчас идёт <b>нечётная</b> неделя\n"
            else:
                timetable_message += "Сейчас идёт <b>чётная</b> неделя\n"
            timetable_message += '\n\t\t\t\t\t\t\t\t\t<b>Понедельник</b>\n\t\t~~~~~~~~~~~~~~~~~~~'
            for i in adding:
                if i[0] == '1':
                    if i[4] == '' and i[5] == '':
                        timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]})\n'
                    else:
                        timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]}) \n{i[4]}\n<b>{i[5]}</b>\n'
        else:
            timetable_message += 'Пар нет!\n Отличный повод увидеться с друзьями! 🎉'
        await msg.reply(timetable_message, parse_mode="HTML")

    elif switch_text == "вторник":
        timetable_message = ""

        url = 'https://edu.sfu-kras.ru/timetable'
        response = requests.get(url).text
        match = re.search(r'Идёт\s\w{8}\sнеделя', response)
        if match:
            current_week = "1"
        else:
            current_week = "2"
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT chat_id, user_group FROM users")
        result_set = cursor.fetchall()
        cursor.close()
        for i in result_set:
            if i[0] == msg.from_user.id:
                group = i[1]
        url = (f'http://edu.sfu-kras.ru/api/timetable/get?target={group}')
        response = requests.get(url).json()
        adding = []
        for item in response["timetable"]:
            if item["week"] == current_week:
                adding.append(
                    [item['day'], item['time'], item['subject'], item['type'], item['teacher'], item['place']])
        flag = 0
        for i in adding:
            if i[0] == '2':
                if i[2] != '':
                    flag = 1
        if flag == 1:
            if match:
                timetable_message += "Сейчас идёт <b>нечётная</b> неделя\n"
            else:
                timetable_message += "Сейчас идёт <b>чётная</b> неделя\n"
            timetable_message += '\n\t\t\t\t\t\t\t\t\t<b>Вторник</b>\n\t\t~~~~~~~~~~~~~~~~~~~'
            for i in adding:
                if i[0] == '2':
                    if i[4] == '' and i[5] == '':
                        timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]})\n'
                    else:
                        timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]}) \n{i[4]}\n<b>{i[5]}</b>\n'
        else:
            timetable_message += 'Пар нет! Отличный повод увидеться с друзьями! 🎉'
        await msg.reply(timetable_message, parse_mode="HTML")

    elif switch_text == "среда":
        timetable_message = ""

        url = 'https://edu.sfu-kras.ru/timetable'
        response = requests.get(url).text
        match = re.search(r'Идёт\s\w{8}\sнеделя', response)
        if match:
            current_week = "1"
        else:
            current_week = "2"
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT chat_id, user_group FROM users")
        result_set = cursor.fetchall()
        cursor.close()
        for i in result_set:
            if i[0] == msg.from_user.id:
                group = i[1]
        url = (f'http://edu.sfu-kras.ru/api/timetable/get?target={group}')
        response = requests.get(url).json()
        adding = []
        for item in response["timetable"]:
            if item["week"] == current_week:
                adding.append(
                    [item['day'], item['time'], item['subject'], item['type'], item['teacher'], item['place']])
        flag = 0
        for i in adding:
            if i[0] == '3':
                if i[2] != '':
                    flag = 1
        if flag == 1:
            if match:
                timetable_message += "Сейчас идёт <b>нечётная</b> неделя\n"
            else:
                timetable_message += "Сейчас идёт <b>чётная</b> неделя\n"
            timetable_message += '\n\t\t\t\t\t\t\t\t\t<b>Среда</b>\n\t\t~~~~~~~~~~~~~~~~~~~'
            for i in adding:
                if i[0] == '3':
                    if i[4] == '' and i[5] == '':
                        timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]})\n'
                    else:
                        timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]}) \n{i[4]}\n<b>{i[5]}</b>\n'
        else:
            timetable_message += 'Пар нет! Отличный повод увидеться с друзьями! 🎉'
        await msg.reply(timetable_message, parse_mode="HTML")

    elif switch_text == "четверг":
        timetable_message = ""

        url = 'https://edu.sfu-kras.ru/timetable'
        response = requests.get(url).text
        match = re.search(r'Идёт\s\w{8}\sнеделя', response)
        if match:
            current_week = "1"
        else:
            current_week = "2"
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT chat_id, user_group FROM users")
        result_set = cursor.fetchall()
        cursor.close()
        for i in result_set:
            if i[0] == msg.from_user.id:
                group = i[1]
        url = (f'http://edu.sfu-kras.ru/api/timetable/get?target={group}')
        response = requests.get(url).json()
        adding = []
        for item in response["timetable"]:
            if item["week"] == current_week:
                adding.append(
                    [item['day'], item['time'], item['subject'], item['type'], item['teacher'], item['place']])
        flag = 0
        for i in adding:
            if i[0] == '4':
                if i[2] != '':
                    flag = 1
        if flag == 1:
            if match:
                timetable_message += "Сейчас идёт <b>нечётная</b> неделя\n"
            else:
                timetable_message += "Сейчас идёт <b>чётная</b> неделя\n"
            timetable_message += '\n\t\t\t\t\t\t\t\t\t<b>Четверг</b>\n\t\t~~~~~~~~~~~~~~~~~~~'
            for i in adding:
                if i[0] == '4':
                    if i[4] == '' and i[5] == '':
                        timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]})\n'
                    else:
                        timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]}) \n{i[4]}\n<b>{i[5]}</b>\n'
        else:
            timetable_message += 'Пар нет! Отличный повод увидеться с друзьями! 🎉'
        await msg.reply(timetable_message, parse_mode="HTML")

    elif switch_text == "пятница":
        timetable_message = ""

        url = 'https://edu.sfu-kras.ru/timetable'
        response = requests.get(url).text
        match = re.search(r'Идёт\s\w{8}\sнеделя', response)
        if match:
            current_week = "1"
        else:
            current_week = "2"
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT chat_id, user_group FROM users")
        result_set = cursor.fetchall()
        cursor.close()
        for i in result_set:
            if i[0] == msg.from_user.id:
                group = i[1]
        url = (f'http://edu.sfu-kras.ru/api/timetable/get?target={group}')
        response = requests.get(url).json()
        adding = []
        for item in response["timetable"]:
            if item["week"] == current_week:
                adding.append(
                    [item['day'], item['time'], item['subject'], item['type'], item['teacher'], item['place']])
        flag = 0
        for i in adding:
            if i[0] == '5':
                if i[2] != '':
                    flag = 1
        if flag == 1:
            if match:
                timetable_message += "Сейчас идёт <b>нечётная</b> неделя\n"
            else:
                timetable_message += "Сейчас идёт <b>чётная</b> неделя\n"
            timetable_message += '\n\t\t\t\t\t\t\t\t\t<b>Пятница</b>\n\t\t~~~~~~~~~~~~~~~~~~~'
            for i in adding:
                if i[0] == '5':
                    if i[4] == '' and i[5] == '':
                        timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]})\n'
                    else:
                        timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]}) \n{i[4]}\n<b>{i[5]}</b>\n'
        else:
            timetable_message += 'Пар нет! Отличный повод увидеться с друзьями! 🎉'
        await msg.reply(timetable_message, parse_mode="HTML")

    elif switch_text == "суббота":
        timetable_message = ""

        url = 'https://edu.sfu-kras.ru/timetable'
        response = requests.get(url).text
        match = re.search(r'Идёт\s\w{8}\sнеделя', response)
        if match:
            current_week = "1"
        else:
            current_week = "2"
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT chat_id, user_group FROM users")
        result_set = cursor.fetchall()
        cursor.close()
        for i in result_set:
            if i[0] == msg.from_user.id:
                group = i[1]
        url = (f'http://edu.sfu-kras.ru/api/timetable/get?target={group}')
        response = requests.get(url).json()
        adding = []
        for item in response["timetable"]:
            if item["week"] == current_week:
                adding.append(
                    [item['day'], item['time'], item['subject'], item['type'], item['teacher'], item['place']])
        flag = 0
        for i in adding:
            if i[0] == '6':
                if i[2] != '':
                    flag = 1
        if flag == 1:
            if match:
                timetable_message += "Сейчас идёт <b>нечётная</b> неделя\n"
            else:
                timetable_message += "Сейчас идёт <b>чётная</b> неделя\n"
            timetable_message += '\n\t\t\t\t\t\t\t\t\t<b>Суббота</b>\n\t\t~~~~~~~~~~~~~~~~~~~'
            for i in adding:
                if i[0] == '6':
                    if i[4] == '' and i[5] == '':
                        timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]})\n'
                    else:
                        timetable_message += f'\n{i[1]}\n{i[2]} ({i[3]}) \n{i[4]}\n<b>{i[5]}</b>\n'
        else:
            timetable_message += 'Пар нет! Отличный повод увидеться с друзьями! 🎉'
        await msg.reply(timetable_message, parse_mode="HTML")
    # Регистрация
    elif switch_text == "регистрация":
        state = dp.current_state(user=msg.from_user.id)
        await state.set_state(Register.all()[0])
        await msg.reply("Ну начнем знакомство! 😉\nВведите ваше ФИО:")

    elif switch_text == "админ-панель":
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        is_succeed = False
        for item in result_set:
            if item[0] == msg.from_user.id:
                is_succeed = True
        if is_succeed:
            state = dp.current_state(user=msg.from_user.id)
            await state.set_state(AdminPanel.all()[0])
            await msg.reply("Добро пожаловать в админ-панель!", reply_markup=KeyBoards.admin_panel)
        else:
            await msg.reply("Вы не являетесь админом", reply_markup=KeyBoards.menu_admin_kb)
    elif switch_text == "меню":
        is_succeed = False
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM admins")
        result_set = cursor.fetchall()
        cursor.close()
        for item in result_set:
            if item[0] == msg.from_user.id:
                is_succeed = True
        if is_succeed:
            await msg.reply('Вы в меню! ✨'
                            , reply=False, reply_markup=KeyBoards.menu_admin_kb)
            conn.commit()
            conn.close()
            state = dp.current_state(user=msg.from_user.id)
            await state.reset_state()
        else:
            await msg.reply('Вы в меню! ✨'
                            , reply=False, reply_markup=KeyBoards.menu_user_kb)
            conn.commit()
            conn.close()

    elif switch_text == "рассылки":
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM mail")
        result_set = cursor.fetchall()
        a = ""
        cursor.close()
        for item in result_set:
            if item[0] == msg.from_user.id:
                local_time = time.ctime(item[2])
                a = a + item[1] + '\n' + 'Эта рассылка заканчивается: ' + local_time + '\n'
        await msg.reply(f"Ваши последние рассылки ✉:\n\n{a}", reply_markup=KeyBoards.mailing_lists_kb)

    elif switch_text == "профиль":
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT chat_id, real_name, user_group FROM users")
        result_set = cursor.fetchall()
        for i in result_set:
            if i[0] == msg.from_user.id:
                await bot.send_message(msg.from_user.id, f"Ваше ФИО: {i[1]}\n"
                                                         f"Ваша группа: {i[2]}")
        conn.commit()
        conn.close()
    elif switch_text == "настройки":
        await msg.reply("Вы в настройках ⚙", reply_markup=KeyBoards.setting_kb)

    elif switch_text == "запланированные мероприятия":
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM times")
        result_set = cursor.fetchall()
        a = "Ваши мероприятия: \n"
        for item in result_set:
            if item[0] == msg.from_user.id:
                local_time = time.ctime(item[2])
                a = a + item[1] + '\n' + 'Это мероприятие заканчивается: ' + local_time + '\n'
        await msg.reply(a, reply_markup=KeyBoards.events_kb)

    elif switch_text == "изменить информацию":
        await msg.reply("Выберите, что хотите изменить 👇", reply_markup=KeyBoards.change_information_kb)

    elif switch_text == "добавить мероприятие":
        state = dp.current_state(user=msg.from_user.id)
        await state.set_state(Events.all()[0])
        await msg.reply("Введите ваше мероприятие 🍻", reply_markup=KeyBoards.universal_kb)

    elif switch_text == "назад":
        await msg.reply("Вы в настройках ⚙", reply_markup=KeyBoards.setting_kb)

    # Изменение имени
    elif switch_text == "изменить имя":
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT chat_id, real_name FROM users")
        result_set = cursor.fetchall()
        for i in result_set:
            if i[0] == msg.from_user.id:
                await bot.send_message(msg.from_user.id, f"Ваше ФИО: {i[1]}\n")
        conn.commit()
        conn.close()
        state = dp.current_state(user=msg.from_user.id)
        await state.set_state(Change.all()[0])
        await bot.send_message(msg.from_user.id, "Введите ваше ФИО 👇")
    # Изменение группы
    elif switch_text == "изменить группу":
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT chat_id, user_group, school, course FROM users")
        result_set = cursor.fetchall()
        for i in result_set:
            if i[0] == msg.from_user.id:
                await bot.send_message(msg.from_user.id,
                                       f"Ваш институт: {i[2]}\nВаш курс: {i[3]}\nВаша группа: {i[1]}\n")
        conn.commit()
        conn.close()
        state = dp.current_state(user=msg.from_user.id)
        await state.set_state(Register.all()[1])
        await msg.reply("Выберите ваш институт 👇", reply_markup=KeyBoards.institute_kb)

    elif switch_text == "посмотреть расписание другой группы":
        await msg.reply("Выберите институт: 🎓", reply_markup=KeyBoards.institute_kb)
        state = dp.current_state(user=msg.from_user.id)
        await state.set_state(ScheduleUser.all()[0])

    elif switch_text == "поддержка разработчиков":
        state = dp.current_state(user=msg.from_user.id)
        await state.set_state(Pay.all()[0])
        await msg.reply("Разработчики благодарны вам, что вы используете их телеграм-бота. Спасибо вам! 😘"
                        , reply_markup=KeyBoards.developer_support_kb)


class MyThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        global adding
        while not self.stopped.wait(3):
            conn = sqlite3.connect('db.db')

            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM `times` WHERE `time` <=  strftime('%s', 'now') + 1800;")
            result_set30 = cursor.fetchall()
            for item in result_set30:
                cursor.execute(f"SELECT `30min` FROM `times` WHERE (`chat_id` = {item[0]} AND `event1` = '{item[1]}');")
                state = cursor.fetchall()
                if state[0][0] == 1:
                    cursor.execute(
                        f"UPDATE `times` SET `30min`= {0} WHERE (`chat_id` = {item[0]} AND `event1` = '{item[1]}');")
                    bot2.send_message(item[0], f'Мероприятие: {item[1]} состоится через пол часа')

            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM `times` WHERE `time` <=  strftime('%s', 'now') + 300;")
            result_set5 = cursor.fetchall()
            for item in result_set5:
                cursor.execute(f"SELECT `5min` FROM `times` WHERE (`chat_id` = {item[0]} AND `event1` = '{item[1]}');")
                state = cursor.fetchall()
                if state[0][0] == 1:
                    cursor.execute(
                        f"UPDATE `times` SET `5min`= {0} WHERE (`chat_id` = {item[0]} AND `event1` = '{item[1]}');")
                    bot2.send_message(item[0], f'Мероприятие: {item[1]} состоится через пять минут')

            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM `times` WHERE `time` <=  strftime('%s', 'now');")
            result_set = cursor.fetchall()
            cursor.execute(f"DELETE FROM `times` WHERE `time` <=  strftime('%s', 'now');")
            conn.commit()
            for item in result_set:
                bot2.send_message(item[0], f'Ваше мероприятие: {item[1]}\nокончено')

            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM `mail` WHERE `time` <=  strftime('%s', 'now') + 1800;")
            result_set30 = cursor.fetchall()
            for item in result_set30:
                cursor.execute(f"SELECT `30min` FROM `mail` WHERE (`chat_id` = {item[0]} AND `event1` = '{item[1]}');")
                state = cursor.fetchall()
                if state[0][0] == 1:
                    cursor.execute(
                        f"UPDATE `mail` SET `30min`= {0} WHERE (`chat_id` = {item[0]} AND `event1` = '{item[1]}');")
                    bot2.send_message(item[0], f'Рассылка: {item[1]} состоится через пол часа')

            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM `mail` WHERE `time` <=  strftime('%s', 'now') + 300;")
            result_set5 = cursor.fetchall()
            for item in result_set5:
                cursor.execute(f"SELECT `5min` FROM `mail` WHERE (`chat_id` = {item[0]} AND `event1` = '{item[1]}');")
                state = cursor.fetchall()
                if state[0][0] == 1:
                    cursor.execute(
                        f"UPDATE `mail` SET `5min`= {0} WHERE (`chat_id` = {item[0]} AND `event1` = '{item[1]}');")
                    bot2.send_message(item[0], f'Рассылка: {item[1]} состоится через пять минут')

            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM `mail` WHERE `time` <=  strftime('%s', 'now');")
            result_set_del = cursor.fetchall()
            cursor.execute(f"DELETE FROM `mail` WHERE `time` <=  strftime('%s', 'now');")
            conn.commit()
            conn.close()
            for item in result_set_del:
                bot2.send_message(item[0], f'Рассылка: {item[1]} закончилась')


class MyThread2(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        global adding
        while not self.stopped.wait(60):
            url = 'https://edu.sfu-kras.ru/timetable'
            response = requests.get(url).text
            match = re.search(r'Идёт\s\w{8}\sнеделя', response)
            if match:
                current_week = "1"
            else:
                current_week = "2"
            conn = sqlite3.connect('db.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT user_group FROM users")
            result_set = cursor.fetchall()
            cursor.close()
            listing = []
            for i in result_set:
                listing.append(i)
            listing = list(set(listing))
            for i in listing:
                url = f'http://edu.sfu-kras.ru/api/timetable/get?target={i[0]}'
                response = requests.get(url).json()
                adding = []
                date = datetime.datetime.today()
                date_date = date.strftime('%H:%M')
                date_split = date_date.split(':')
                listing_date_split = []
                for n in date_split:
                    n = int(n)
                    listing_date_split.append(n)
                listing_date_sum = listing_date_split[0]*60+listing_date_split[1]
                for item in response["timetable"]:
                    if item["week"] == current_week:
                        adding.append(
                            [item['day'], item['time'], item['subject'], item['type'], item['teacher'], item['place']])
                date1 = datetime.datetime.today()
                now = datetime.datetime.weekday(date1)+1
                for j in adding:
                    if int(j[0]) == now:
                        a = j[1].split('-')
                        if date_date == a[0]:
                            conn = sqlite3.connect('db.db')
                            cursor = conn.cursor()
                            cursor.execute(f"SELECT chat_id FROM users WHERE user_group = '{i[0]}'")
                            id_group = cursor.fetchall()
                            cursor.close()
                            for k in id_group:
                                bot2.send_message(k, f'У вас началась {j[2]}')
                        date_kur = a[0].split(':')
                        listing_date = []
                        for n in date_kur:
                            n = int(n)
                            listing_date.append(n)
                        listing_date_sum2 = listing_date[0] * 60 + listing_date[1]
                        if listing_date_sum == listing_date_sum2 - 5:
                            conn = sqlite3.connect('db.db')
                            cursor = conn.cursor()
                            cursor.execute(f"SELECT chat_id FROM users WHERE user_group = '{i[0]}'")
                            id_group = cursor.fetchall()
                            cursor.close()
                            for k in id_group:
                                bot2.send_message(k, f'У вас через 5 минут начнется {j[2]}')


if __name__ == "__main__":
    stopFlag = threading.Event()
    thread = MyThread(stopFlag)
    thread.start()
    stopFlag2 = threading.Event()
    thread2 = MyThread2(stopFlag2)
    thread2.start()
    executor.start_polling(dp, on_shutdown=shutdown)


# руссификация дат, парсинг кнопок
