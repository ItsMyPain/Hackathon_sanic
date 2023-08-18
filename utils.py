import secrets
import string
from asyncio import get_event_loop
from typing import Tuple
from uuid import uuid4

from bcrypt import hashpw, gensalt, checkpw
from sanic import Sanic, json, Request
from sanic.request import File
from sanic.response import JSONResponse
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSessionTransaction


async def load_file(app: Sanic, Bucket: str, files: File | list[File], directory: str = '') -> str | list[str]:
    """
    Загружает файлы в bucket.
    :param directory:   Папка, / только на конце
    :param app:         Приложение.
    :param Bucket:      Название bucket.
    :param files:       Файл или лист файлов.
    :return:            Адрес или лист адресов файлов.
    """
    if directory:
        path = f'https://storage.yandexcloud.net/{Bucket}/{directory}'
    else:
        path = f'https://storage.yandexcloud.net/{Bucket}/'
    async with app.ctx.S3_SESSION.client(service_name='s3',
                                         endpoint_url='https://storage.yandexcloud.net') as s3:
        if isinstance(files, list):
            filenames = []
            for file in files:
                filename = file.name + uuid4().hex + '.' + file.name.split('.')[-1]
                await s3.put_object(Bucket=Bucket, Key=directory + filename, Body=file.body)
                filenames.append(path + filename)
        else:
            filename = files.name + uuid4().hex + '.' + files.name.split('.')[-1]
            await s3.put_object(Bucket=Bucket, Key=directory + filename, Body=files.body)
            filenames = path + filename

    return filenames


async def delete_file(app: Sanic, Bucket: str, files: str | list[str]):
    """
    Удаляет файлы из bucket.
    :param app:     Приложение.
    :param files:   Файл или лист файлов.
    :param Bucket:  Название bucket.
    :return:
    """
    print(files)


def response(data=None, code: int = None, meta: list | dict = None) -> JSONResponse:
    """
    Генерация ответа.
    :param meta:    Метаданные.
    :param data:    Данные для ответа или ошибки.
    :param code:    Код ошибки.
    :return:
    """
    if data is None:
        data = {}
    if code is None:
        if meta is None:
            return json({'data': data})
        else:
            return json({'data': data, 'meta': meta})
    return json({'data': None, 'errors': [{'code': code, 'message': data}]}, code)


async def hash_password(password: str) -> bytes:
    """
    Хеширование пароля с использованием bcrypt.
    :param password:
    :return:
    """
    return await get_event_loop().run_in_executor(None, hashpw, password.encode(), gensalt())


async def check_password(password: str, hashed_password: bytes) -> bool:
    """
    Проверка пароля с использованием bcrypt.
    :param hashed_password:
    :param password:
    :return:
    """
    return await get_event_loop().run_in_executor(None, checkpw, password.encode(), hashed_password)


async def generate_password() -> str:
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))


async def parse_key(key: str) -> Tuple[str, str]:
    """
    Парсинг ключа.
    :param key:
    :return:
    """
    idx = key.rfind('__')
    if idx == -1:
        return key, ''
    return key[:idx], key[idx + 2:]


def get_main(company: Row):
    main_view = {
        1: 'table',
        2: 'cards'
    }
    filter_view = {
        1: 'vertical',
        2: 'modal'
    }
    return f"main/{filter_view[company.filter_view]}_{main_view[company.main_view]}.html"


def get_name(data) -> str:
    return data.first_name.capitalize() + ' ' + data.last_name[0].upper() + '.'
