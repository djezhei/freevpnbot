from aiogram.utils.keyboard import InlineKeyboardBuilder

from settings import donation_values


# /start kb for new users
start_noname_builder = InlineKeyboardBuilder()
start_noname_builder.button(text='\U000023F3 Подключиться', callback_data='my_sub')
start_noname_builder.button(text='\U0001F499 Пожертвовать', callback_data='buy_sub')
start_noname_builder.button(text='\U0001F193 Промокод', callback_data='promo')
start_noname_builder.adjust(1, repeat=True)

# /start kb for existing users
start_builder = InlineKeyboardBuilder()
start_builder.button(text='\U00002699 Подключиться', callback_data='my_sub')
start_builder.button(text='\U0001F499 Пожертвовать', callback_data='buy_sub')
start_builder.button(text='\U0001F193 Промокод', callback_data='promo')
start_builder.adjust(1, repeat=True)

back_builder = InlineKeyboardBuilder()
back_builder.button(text='<<Назад', callback_data='back')


def get_prices_kb():
    prices_builder = InlineKeyboardBuilder()
    for donation_value in donation_values:
        prices_builder.button(
            text=f'{donation_value} руб.',
            callback_data=f'bs{donation_value}'
        )
    prices_builder.button(text='<<Назад', callback_data='back')
    prices_builder.adjust(1, repeat=True)
    return prices_builder.as_markup()


def get_payment_kb(payment_url: str):
    payment_kb = InlineKeyboardBuilder()
    payment_kb.button(text='Оплатить', url=payment_url)
    payment_kb.button(text='Проверить оплату', callback_data='check_payment')
    payment_kb.button(text='<<Назад', callback_data='back')
    payment_kb.adjust(1, repeat=True)
    return payment_kb.as_markup()
