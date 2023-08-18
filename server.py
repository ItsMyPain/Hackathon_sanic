import json
import os
from contextvars import ContextVar

from dotenv import load_dotenv, find_dotenv
from sanic import Sanic, Request, HTTPResponse
from sanic_ext import render
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import load_config
from views import shop

load_dotenv(find_dotenv())

app = Sanic("my_app")
app.blueprint(shop)

dir_path = os.path.dirname(os.path.realpath(__file__))
app.static('/static', dir_path + r'/static')

bind = create_async_engine(os.getenv("DB_LOCAL"), pool_size=10, pool_pre_ping=True, echo=True)
_session_maker = async_sessionmaker(bind, expire_on_commit=False)
_base_model_session_ctx = ContextVar("session")


@app.middleware("request")
async def inject_session(request: Request):
    request.ctx.session = json.loads(request.cookies.get('session', '{}'))
    request.ctx.db_session = _session_maker()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.db_session)


@app.middleware("response")
async def close_session(request: Request, response: HTTPResponse):
    response.add_cookie('session', json.dumps(request.ctx.session), max_age=60 * 60)
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.db_session.close()


@app.before_server_start
async def init(app1: Sanic):
    load_config(app)

    if not app1.debug:
        @app1.exception(Exception)
        async def catch_anything(request, _):
            return await render('error.html', context=dict(Company=request.app.config.DEFAULT_COMPANY))

    # app1.ctx.SMTP = SMTP(hostname=app1.config.SMTP_HOST, port=app1.config.SMTP_PORT, use_tls=True,
    #                      username=app1.config.SMTP_EMAIL, password=app1.config.SMTP_PSWD)
    # pprint(f'Подключение к SMTP: {app1.ctx.SMTP.hostname}')


@app.before_server_stop
async def stop(app1: Sanic):
    await app1.ctx.POOL.dispose()
    # app1.ctx.SMTP.close()


if __name__ == '__main__':
    app.run(dev=True, workers=2)
