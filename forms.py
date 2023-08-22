from sanic_wtf import SanicForm
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from wtforms import PasswordField, StringField, EmailField, FileField
from wtforms.validators import DataRequired, Email, EqualTo

from models import Users


class BaseUserForm(SanicForm):
    username = StringField(label="Юзернейм", render_kw={"placeholder": "elf_lesnoy", "autofocus": True},
                           validators=[DataRequired('Поле не может быть пустым')])
    email = EmailField(label="Почта", render_kw={"placeholder": "invanov@elflesnoy.ru"},
                       validators=[Email('Неправильная почта')])

    async def check_data(self, session: AsyncSession, user_id: int = None):
        data = (
            await session.execute(
                select(Users.user_id)
                .where(or_(Users.email == self.email.data, Users.username == self.username.data))
            )
        ).first()
        if (data is None) or (data is not None and user_id is not None and user_id == data.user_id):
            return True

        self.email.errors.append('Почта или юзернейм уже заняты')
        return False


class PhotoForm(SanicForm):
    photo = FileField(label='Фото вашего лица',
                      render_kw={"onChange": "myFunc(this)", "accept": "image/png, image/jpeg"})


class PasswordsForm(SanicForm):
    password1 = PasswordField(label="Пароль", render_kw={"placeholder": "111111"},
                              validators=[DataRequired('Поле не может быть пустым')])
    password2 = PasswordField(label="Подтверждение пароля", render_kw={"placeholder": "111111"},
                              validators=[EqualTo('password1', 'Пароли не совпадают')])


class ChangePasswordForm(PasswordsForm):
    old_password = PasswordField(label="Старый пароль", render_kw={"placeholder": "111111"},
                                 validators=[DataRequired('Поле не может быть пустым')])


class LoginForm(SanicForm):
    login = StringField(label="Почта или юзернейм",
                        render_kw={"placeholder": "invanov@elflesnoy.ru", "autofocus": True},
                        validators=[DataRequired('Поле не может быть пустым')])
    password = PasswordField(label="Пароль", render_kw={"placeholder": "111111"},
                             validators=[DataRequired('Поле не может быть пустым')])


class RegistrationForm(BaseUserForm, PasswordsForm, PhotoForm):
    pass
