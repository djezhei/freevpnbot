import asyncio
from datetime import datetime
import logging
import sys
from time import time

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
# from aiogram.methods.delete_message import DeleteMessage
from aiogram.types import Message
from sqlalchemy import insert, select, update

from db import give_sub_to_user, session as s
import payments
from models import User, Promo, UsedPromo
from settings import TG_TOKEN, sub_types
import tg_kbs as kb


dp = Dispatcher()


LAST_MESSAGE: Message   # TODO хранить LAST_MESSAGE в бд, после перезапуска удаляется, очевидно


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user = s.get(User, message.from_user.id)
    message_text = f'Привет, {message.from_user.username}'
    if user:
        if user.is_active:
            message_text += (f'\nПодписка <b>активна еще <u>'
                             f'{datetime.utcfromtimestamp(user.end_on - int(time())).strftime("%M")} минут</u></b>')
            markup = kb.start_builder.as_markup()
        elif user.end_on:
            message_text += (f'\nПодписка <b>закончилась.<u>'
                             f'</u></b>Активируйте новую чтобы продолжить пользоваться интернетом без ограничений')
            markup = kb.start_builder.as_markup()
    else:
            message_text += f'\nПопробуй подключиться - <b>это бесплатно</b>'
            markup = kb.start_noname_builder.as_markup()
    await message.delete()
    global LAST_MESSAGE
    LAST_MESSAGE = await message.answer(message_text, reply_markup=markup)


@dp.callback_query(lambda c: c.data == 'back')
async def back_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    user = s.get(User, callback_query.from_user.id)
    message_text = f'Привет, {callback_query.from_user.username}'
    if user:
        if user.is_active:
            message_text += (f'\nПодписка <b>активна еще <u>'
                             f'{datetime.utcfromtimestamp(user.end_on - int(time())).strftime("%M")} минут</u></b>')
            markup = kb.start_builder.as_markup()
        elif user.end_on:
            message_text += (f'\nПодписка <b>закончилась.<u>'
                             f'</u></b>Активируйте новую чтобы продолжить пользоваться интернетом без ограничений')
            markup = kb.start_builder.as_markup()
    else:
            message_text += f'\nПопробуй подключиться - <b>это бесплатно</b>'
            markup = kb.start_noname_builder.as_markup()
    await callback_query.message.edit_text(message_text, reply_markup=markup)


@dp.callback_query(lambda c: c.data == 'my_sub')
async def get_my_sub(callback_query: types.CallbackQuery):
    await callback_query.answer()
    user = s.get(User, callback_query.from_user.id)
    if user.is_active:
        await callback_query.message.edit_text(
            f'<b>Ключ</b> для подключения:\n\n<code>{user.vpn_url}</code>\n\n<a href="https://telegra.ph/Podklyuchenie'
            '-na-iOS-11-20">Подключение на iOS</a>\n'
            '<a href="https://telegra.ph/Podklyuchenie-na-Android-11-20">Подключение на Android</a>',
            disable_web_page_preview=True,
            reply_markup=kb.back_builder.as_markup(),
        )
    else:
        give_sub_to_user(callback_query.from_user.id, 0)
        await get_my_sub(callback_query)


@dp.callback_query(lambda c: c.data == 'buy_sub')
async def get_prices_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    reply_text = 'Выберите <b>сумму пожертвования</b>'
    await callback_query.message.edit_text(reply_text, reply_markup=kb.get_prices_kb())


@dp.callback_query(lambda c: c.data[:2] == 'bs')
async def buy_sub_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    sub_cost = int(callback_query.data[2:])
    payment_url = payments.create_payment_form(callback_query.from_user.id, sub_cost)
    await callback_query.message.edit_text(
        f'</b>\nК оплате: <b>{sub_cost}</b> руб.',
        reply_markup=kb.get_payment_kb(payment_url)
    )


@dp.callback_query(lambda c: c.data == 'check_payment')
async def check_payment_callback(callback_query: types.CallbackQuery):
    if payments.check_payment(callback_query.from_user.id):
        await callback_query.answer('Спасибо, оплата прошла успешно <3', show_alert=True)
        await back_callback(callback_query)
    else:
        await callback_query.answer('Оплата не выполнена', show_alert=True)


@dp.callback_query(lambda c: c.data == 'promo')
async def promo_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text('Введите промокод', reply_markup=kb.back_builder.as_markup())


@dp.message()
async def catch_promos(message: types.Message):
    user_promo = message.text.upper()
    promo = s.get(Promo, user_promo)
    if promo:
        stmt = select(UsedPromo).where(UsedPromo.user == message.from_user.id).where(UsedPromo.promocode == user_promo)
        is_used = s.execute(stmt).one_or_none()
        if is_used:
            await message.delete()
            await LAST_MESSAGE.edit_text(
                f'\U00002716Промокод <code>{message.text}</code> уже был активирован\nПопробуйте другой',
                reply_markup=kb.back_builder.as_markup()
            )
            return
        ans_text = '\U0001F44CПромокод активирован'
        if promo.discount < 0:
            sub_type = -1 * promo.discount 
            is_url_change = give_sub_to_user(message.from_user.id, sub_type)
            if is_url_change:
                ans_text += '\n<u>Ключ для подключения <b>изменился</b>. Обновите ключ</u>'
        else:
            user = s.get(User, message.from_user.id)
            if not user:
                stmt = insert(User).values(utid=message.from_user.id,is_active=False,discount=promo.discount)
                s.execute(stmt)
            else:
                user.discount = promo.discount
        s.execute(
            insert(UsedPromo).
            values(
                user=message.from_user.id,
                promocode=promo.promocode,
                discount=promo.discount
            )
        )
        s.commit()

        try:
            await LAST_MESSAGE.delete()
        except NameError:
            print('NameError')
        
        ans_message = await message.answer(ans_text)
        await command_start_handler(message)
        await asyncio.sleep(5)
        await ans_message.delete()
    else:
        await message.delete()
        await LAST_MESSAGE.edit_text(
            f'\U00002716Промокод <code>{message.text}</code> не существует\nПопробуйте другой',
            reply_markup=kb.back_builder.as_markup()
        )


async def main() -> None:
    bot = Bot(TG_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR, stream=sys.stdout)
    asyncio.run(main())
