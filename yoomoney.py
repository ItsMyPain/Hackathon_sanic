import os

import var_dump
from dotenv import load_dotenv, find_dotenv
from yookassa import Configuration
from yookassa import Payment

load_dotenv(find_dotenv())
Configuration.configure(os.getenv("YOOKASSA_ID"), os.getenv("YOOKASSA_KEY"))

payment = {
    "amount": {
        "value": "11.00",
        "currency": "RUB"
    },
    "payment_method_data": {
        "type": "bank_card"
    },
    "confirmation": {
        "type": "redirect",
        "return_url": "https://www.example.com/return_url"
    },
    "capture": True,
    "description": "Привязка карты",
    "save_payment_method": True

}
# res = Payment.create(payment)
# var_dump.var_dump(res)

res = Payment.find_one("2c77396d-000f-5000-8000-12aaded2e5be")
var_dump.var_dump(res)

# ment = Payment.create({
#     "amount": {
#         "value": "20.00",
#         "currency": "RUB"
#     },
#     "capture": True,
#     "payment_method_id": "2c77396d-000f-5000-8000-12aaded2e5be",
#     "description": "Заказ №105"
# })
# var_dump.var_dump(ment)
# 2c77396d-000f-5000-8000-12aaded2e5be
