import json
from urllib.parse import unquote

from sanic import Blueprint, Request, redirect
from sanic_ext import render
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from auth import login_user, login_optional
from forms import LoginForm, RegistrationForm
from models import Users
from utils import check_password

shop = Blueprint("shop")


@shop.route("/registration", methods=['POST', 'GET'])
async def registration(request: Request):
    form = RegistrationForm(request)
    if form.validate_on_submit():
        session: AsyncSession = request.ctx.db_session
        async with session.begin():
            data = (
                await session.execute(
                    select(Users.user_id, Users.password)
                    .where(or_(Users.email == form.email.data, Users.username == form.username.data))
                )
            ).first()
            if data is not None:
                form.email.errors.append('Почта или юзернейм уже заняты')
            else:
                pass
                # print(form.data)
        # user_id = (
        #     await session.execute(
        #         insert(Users)
        #         .values(username=form.username.data,
        #                 email=form.email.data,
        #                 password=await hash_password(form.password1.data))
        #         .returning(Users.user_id)
        #     )
        # ).scalar()
        # return await login_user(request, redirect(request.app.url_for('shop.main_page')), user_id)

    return await render('registration.html', context=dict(form=form))


@shop.route("/login", methods=['POST', 'GET'])
async def login(request: Request):
    form = LoginForm(request)
    if form.validate_on_submit():
        session: AsyncSession = request.ctx.db_session
        async with session.begin():
            data = (
                await session.execute(
                    select(Users.user_id, Users.password)
                    .where(or_(Users.email == form.login.data, Users.username == form.login.data))
                )
            ).first()
            if data is None or not await check_password(form.password.data, data.password):
                form.login.errors.append('Неправильный логин или пароль')
            else:
                return await login_user(request, redirect(request.app.url_for('shop.main_page')), data.user_id)

    return await render('login.html', context=dict(form=form))


@shop.get("/")
@login_optional
async def main_page(request: Request, user_id: int | bool):
    cart_items = json.loads(unquote(request.cookies.get('cart', '{}')))
    return await render('main_page.html', context=dict(cart=cart_items))


@shop.get("/cart")
@login_optional
async def cart(request: Request, user_id: int | bool):
    return await render('base.html')
