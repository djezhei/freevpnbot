from sqlalchemy import create_engine, delete, select, insert
from sqlalchemy.orm import Session
from typing import Union
from time import time

import api
from settings import REFERAL_DISCOUNT, DB_LINK, sub_types
from models import Base, User, ProxyServer
from notifications import send_tg_message


engine = create_engine(DB_LINK, echo=True)
session = Session(engine)
Base.metadata.create_all(engine)


def give_sub_to_user(utid: int, sub_type: int) -> Union[None, bool]:
    """
    Renewing a subscription or creating a new one.
    Add client to proxy server if required.
    Return True if user vpn_url is changed.
    """
    user = session.get(User, utid)
    if user:
        if user.is_active:
            user.end_on += sub_types[sub_type]['seconds']
        else:
            server = session.scalar(select(ProxyServer).order_by(ProxyServer.users_count).limit(1))
            vpn_url = api.add_vless_client(str(utid), server)
            server.users_count += 1
            user.is_active = True
            user.end_on = int(time()) + sub_types[sub_type]['seconds']
            user.proxy_server = server.id
            user.vpn_url = vpn_url
            session.commit()
            return True
    else:
        server = session.scalar(select(ProxyServer).order_by(ProxyServer.users_count).limit(1))
        vpn_url = api.add_vless_client(str(utid), server)
        server.users_count += 1
        session.execute(
            insert(User).
            values(
                utid=utid,
                is_active=True,
                end_on=int(time()) + sub_types[sub_type]['seconds'],
                proxy_server=server.id,
                vpn_url=vpn_url
            )
        )
    session.commit()
