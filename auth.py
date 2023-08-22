from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Callable

import jwt
from jwt import InvalidTokenError
from jwt import encode
from sanic import Request, redirect
from sanic.response import HTTPResponse
from sqlalchemy import select

from models import Users


async def login_user(request: Request, _response: HTTPResponse, user_id: int) -> HTTPResponse:
    _response.add_cookie(
        key="SANIC_TOKEN",
        value=encode(
            payload={
                'user_id': str(user_id),
                'exp': datetime.now(tz=timezone.utc) + timedelta(seconds=request.app.config.TOKEN_TIME),
                'iss': 'platform'},
            key=request.app.config.SECRET_KEY),
        httponly=request.app.config.HTTPONLY_COOKIES,
        secure=request.app.config.SECURE_COOKIES,
        max_age=request.app.config.TOKEN_TIME
    )
    return _response


async def logout_user(_response: HTTPResponse) -> HTTPResponse:
    _response.delete_cookie("SANIC_TOKEN")
    return _response


def login_required(wrapped: Callable):
    def decorator(func):
        @wraps(func)
        async def decorated_function(request):
            token = request.cookies.get("SANIC_TOKEN", False)
            uid = await check_token(request, token, 'platform', 'user_id')
            if uid:
                return await func(request, uid)
            else:
                return redirect(request.app.url_for('shop.login'))

        return decorated_function

    return decorator(wrapped)


def logout_required(wrapped: Callable):
    def decorator(func):
        @wraps(func)
        async def decorated_function(request):
            token = request.cookies.get("SANIC_TOKEN", False)
            uid = await check_token(request, token, 'platform', 'user_id')
            if uid:
                return redirect(request.app.url_for('shop.main_page'))
            else:
                return await func(request)

        return decorated_function

    return decorator(wrapped)


def login_optional(wrapped: Callable):
    def decorator(func):
        @wraps(func)
        async def decorated_function(request, **kwargs):
            token = request.cookies.get("SANIC_TOKEN", False)
            uid = await check_token(request, token, 'platform', 'user_id')
            return await func(request, uid, **kwargs)

        return decorated_function

    return decorator(wrapped)


async def check_token(request: Request, token: str, issuer: str, key: str) -> bool | int:
    if not token:
        return False

    try:
        data = jwt.decode(token, request.app.config.SECRET_KEY, algorithms=["HS256"], issuer=issuer)
        user_id = int(data.get(key, 'id'))
    except InvalidTokenError or ValueError:
        return False

    session = request.ctx.db_session
    async with session.begin():
        if (await session.execute(select(Users.user_id).where(Users.user_id == user_id))).scalar() is None:
            return False

    return user_id
