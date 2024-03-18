from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.types import BigInteger
from time import time
from typing import Any
from uuid import UUID, uuid4


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    utid: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True, nullable=False)
    is_active: Mapped[bool]
    end_on: Mapped[int] = mapped_column(BigInteger, nullable=True)
    proxy_server: Mapped[int] = mapped_column(ForeignKey('proxy_servers.id'), nullable=True)
    vpn_url: Mapped[str] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f'User: {self.utid=}, {self.is_active=}, {self.vpn_url=}'


class Payment(Base):
    __tablename__ = 'payments'

    uuid: Mapped[UUID] = mapped_column(primary_key=True, unique=True)
    utid: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, default=int(time()))
    purchased_at: Mapped[int] = mapped_column(BigInteger, nullable=True)
    is_purchased: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f'Payment: {self.utid=}, {self.sub_type=}, {self.is_purchased=}'


class Promo(Base):
    __tablename__ = 'promos'

    promocode: Mapped[str] = mapped_column(primary_key=True)
    discount: Mapped[int]

    def __repr__(self) -> str:
        return f'Promo: {self.promocode=}, {self.discount=}'


class UsedPromo(Base):
    __tablename__ = 'used_promos'

    user: Mapped[User] = mapped_column(ForeignKey('users.utid'), primary_key=True)
    promocode: Mapped[str]
    discount: Mapped[int]
    use_at: Mapped[int] = mapped_column(BigInteger, default=int(time()))


class ProxyServer(Base):
    __tablename__ = 'proxy_servers'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False, autoincrement=True)
    protocol: Mapped[str] = mapped_column(nullable=False, default='http://')
    host: Mapped[str]
    api_port: Mapped[int]
    client_port: Mapped[int]
    inbound_id: Mapped[int]
    users_count: Mapped[int] = mapped_column(default=0)
    cookie: Mapped[str] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f'ProxyServer: {self.host=}, {self.api_port=}, {self.users_count=}'
