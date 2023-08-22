import asyncio
import json
import os
from urllib.parse import unquote
from uuid import uuid4, UUID

import aiofiles
import var_dump
from sanic import Blueprint, Request, redirect, text
from sanic.request import File
from sanic_ext import render
from sqlalchemy import select, or_, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa import Payment

from auth import login_user, login_optional, login_required, logout_user
from forms import LoginForm, RegistrationForm, BaseUserForm, PhotoForm
from models import Users, Payments
from utils import check_password, hash_password

shop = Blueprint("shop")


@shop.route("/registration", methods=['POST', 'GET'])
# @logout_required
async def registration(request: Request):
    form = RegistrationForm(request)
    file: File = request.files.get('photo')
    session: AsyncSession = request.ctx.db_session
    async with session.begin():
        if form.validate_on_submit() and await form.check_data(session):
            filename = f'static/photos/{form.username.data}_{uuid4().hex}_{file.name}'
            async with aiofiles.open(filename, 'wb') as f:
                await f.write(file.body)
            user_id = (
                await session.execute(
                    insert(Users)
                    .values(username=form.username.data,
                            email=form.email.data,
                            password=await hash_password(form.password1.data),
                            photo=filename)
                    .returning(Users.user_id)
                )
            ).scalar()
            return await login_user(request, redirect(request.app.url_for('shop.main_page')), user_id)

    return await render('registration.html', context=dict(form=form))


@shop.route("/login", methods=['POST', 'GET'])
# @logout_required
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
    username = False
    if user_id:
        session: AsyncSession = request.ctx.db_session
        async with session.begin():
            username = (
                await session.execute(select(Users.username).where(Users.user_id == user_id))
            ).scalar_one()
    return await render('main_page.html', context=dict(cart=cart_items, username=username))


@shop.get("/profile")
@login_required
async def profile_get(request: Request, user_id: int):
    session: AsyncSession = request.ctx.db_session
    async with session.begin():
        data = (
            await session.execute(select("*").select_from(Users).where(Users.user_id == user_id))
        ).one()
    form = BaseUserForm(request, obj=data)
    photo_form = PhotoForm(request)
    return await render('profile.html', context=dict(form=form, photoForm=photo_form,
                                                     username=data.username, user=data))


@shop.post("/profile")
@login_required
async def profile_post(request: Request, user_id: int):
    form = BaseUserForm(request)
    photo_form = PhotoForm(request)
    session: AsyncSession = request.ctx.db_session
    form_data = request.form
    print(form_data)
    async with session.begin():
        if form_data.get('info_submit') and form.validate_on_submit() and await form.check_data(session, user_id):
            await session.execute(
                update(Users).values(username=form.username.data, email=form.email.data).where(Users.user_id == user_id)
            )
            return redirect(request.app.url_for('shop.profile_get'))

        data = (
            await session.execute(select("*").select_from(Users).where(Users.user_id == user_id))
        ).one()

        if form_data.get('photo_submit') and photo_form.validate_on_submit():
            file: File = request.files.get('photo')
            filename = f'static/photos/{data.username}_{uuid4().hex}_{file.name}'
            async with aiofiles.open(filename, 'wb') as f:
                await f.write(file.body)
            await session.execute(
                update(Users).values(photo=filename).where(Users.user_id == user_id)
            )
            try:
                os.remove(data.photo)
            except Exception as e:
                print(e)

            return redirect(request.app.url_for('shop.profile_get'))

        if form_data.get("logout"):
            return await logout_user(redirect(request.app.url_for('shop.main_page')))

        if form_data.get("delete"):
            photo = (await session.execute(
                delete(Users).where(Users.user_id == user_id).returning(Users.photo)
            )).scalar()
            try:
                os.remove(photo)
            except Exception as e:
                print(e)

            return await logout_user(redirect(request.app.url_for('shop.main_page')))

        if form_data.get('add_card'):
            pid = uuid4()
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
                    "return_url": f"http://localhost:8000/add_card/{pid}"
                },
                "capture": True,
                "description": "Привязка карты",
                "save_payment_method": True
            }
            res = Payment.create(payment)
            await session.execute(
                insert(Payments).values(payment_id=pid, user_id=user_id, payment_method_id=res.payment_method.id)
            )
            return redirect(res.confirmation.confirmation_url)

        if form_data.get("delete_card"):
            await session.execute(
                update(Users).values(card=None, payment_method_id=None).where(Users.user_id == user_id)
            )
            return redirect(request.app.url_for('shop.profile_get'))

    return await render('profile.html', context=dict(form=form, photoForm=photo_form,
                                                     username=data.username, user=data))


@shop.get("/cart")
@login_optional
async def cart(request: Request, user_id: int | bool):
    username = False
    if user_id:
        session: AsyncSession = request.ctx.db_session
        async with session.begin():
            username = (
                await session.execute(select(Users.username).where(Users.user_id == user_id))
            ).scalar_one()
    return await render('base.html', context=dict(username=username))


@shop.get("/add_card/<payment_id>")
async def add_card_get(request: Request, payment_id: UUID):
    session: AsyncSession = request.ctx.db_session
    async with session.begin():
        data = (await session.execute(
            select("*").where(Payments.payment_id == payment_id)
        )).first()
        if data is None:
            return text('Что-то пошло не так, обратитесь к администратору')
        await session.execute(
            update(Users).values(state_id=2).where(Payments.payment_id == payment_id)
        )
        while True:
            res = Payment.find_one(data.payment_method_id)
            var_dump.var_dump(res)
            if res.status == 'succeeded':
                break
            await asyncio.sleep(2)

        if not res.payment_method.saved:
            return text('Что-то пошло не так, обратитесь к администратору')

        await session.execute(
            update(Users).values(card=res.payment_method.title, payment_method_id=res.payment_method.id, state_id=3)
            .where(Payments.payment_id == payment_id)
        )
        return redirect(request.app.url_for("shop.profile_get"))
