import os

from sanic import json, Blueprint, Request
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import RequestBody
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from models import Base

admin = Blueprint("admin", url_prefix="/admin")


@admin.post('/create_all')
@openapi.body(RequestBody({"application/json": {'password': str}}), required=True)
async def create_all(request: Request):
    if request.json.get('password', '') != '9a87ed9a-5f30-4b39-b33e-8dacc0093806':
        return json({'msg': 'Неправильный пароль'})

    meta_data = Base.metadata
    bind = create_async_engine(os.getenv("DB_LOCAL"), pool_size=10, pool_pre_ping=True, echo=True)
    async with bind.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.run_sync(meta_data.create_all)

    return json({'msg': 'База данных создана'})


@admin.post('/clear_all')
@openapi.body(RequestBody({"application/json": {'password': str}}), required=True)
async def clear_all(request: Request):
    if request.json.get('password', '') != '9a87ed9a-5f30-4b39-b33e-8dacc0093806':
        return json({'msg': 'Неправильный пароль'}, 401)

    meta_data = Base.metadata
    bind = create_async_engine(os.getenv("DB_LOCAL"), pool_size=10, pool_pre_ping=True, echo=True)
    async with bind.begin() as conn:
        await conn.run_sync(meta_data.drop_all)
        await conn.run_sync(meta_data.create_all)

    return json({'msg': 'База данных очищена'})
