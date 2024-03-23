from sqlalchemy import select
from time import time, sleep

import api
from db import session as s
from models import User
from notifications import send_tg_message, send_service_tg_message


def check_expired_subs() -> None:
    """
    Check users table for any expired subscriptions. Remove it from proxy server
    and database table if expired.
    """
    expired_subs = s.scalars(
        select(User).
        where(
            User.is_active == True,
            User.end_on <= int(time())
        )
    ).all()
    try:
        if expired_subs:
            print(expired_subs)
            for expired_sub in expired_subs:
                api.delete_client(expired_sub.utid, expired_sub.proxy_server)
                send_tg_message(expired_sub.utid, f'❗Время подписки истекло')
                expired_sub.is_active = False
                expired_sub.proxy_server = None
                expired_sub.proxy_server_id = None
                expired_sub.vpn_url = None
            s.commit()
    except Exception as exc:
        send_service_tg_message(f'[err] main/db.py/check_expired_subs', exc)


def start_db_management() -> None:
    """
    Start infinite table data checking and updating
    """
    while True:
        check_expired_subs()
        sleep(60)
