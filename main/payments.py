from sqlalchemy import select, insert, update
from time import time
from uuid import uuid4
from yoomoney import Client, Quickpay

from db import give_sub_to_user, session as s
from models import Payment
from settings import YOO_TOKEN, YOO_RECEIVER, YOO_SUCCESS_URL


def create_payment_form(utid: int, sub_cost: int) -> str:
    """
    Return payment url for user with utid.
    """
    uuid = uuid4()
    s.execute(insert(Payment).values(uuid=uuid, utid=utid))
    s.commit()
    quick_pay = Quickpay(
        receiver=YOO_RECEIVER,
        quickpay_form='shop',
        targets='Sponsor this project',
        paymentType='SB',
        sum=sub_cost,
        label=str(uuid),
        successURL=YOO_SUCCESS_URL
    )
    return quick_pay.redirected_url


def check_payment(utid: int) -> bool:
    """
    Return True if the payment has been completed, False otherwise.
    """
    user_payments = s.scalars(select(Payment).where(Payment.utid == utid).where(Payment.is_purchased == False))
    client = Client(YOO_TOKEN)
    for user_payment in user_payments:
        print(user_payment.uuid)
        history = client.operation_history(label=str(user_payment.uuid))
        for operation in history.operations:
            if operation.status == 'success':
                user_payment.purchased_at = int(time())
                user_payment.is_purchased = True
                s.commit()
                return True
    return False
