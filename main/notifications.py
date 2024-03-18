import requests

from settings import TG_SEND_MESSAGE_URL, TG_SEND_SERVICE_MESSAGE_URL


def send_tg_message(utid:int, text: str) -> None:
    """
    Send a message text from main telegram bot
    """
    try:
        requests.get(TG_SEND_MESSAGE_URL + f'&chat_id={utid}&text={text}')
    except Exception as exc:
        print(exc) # TODO logging


def send_service_tg_message(message: str) -> None:
    """
    Send a message text in service telegram bot to admin.
    """
    try:
        requests.get(TG_SEND_SERVICE_MESSAGE_URL + f'&text={message}')
    except Exception as exc:
        print(exc)  # TODO logging
