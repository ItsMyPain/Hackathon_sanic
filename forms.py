from sanic_wtf import SanicForm
from wtforms import PasswordField, StringField, EmailField, FileField
from wtforms.validators import DataRequired, Email, EqualTo


class LoginForm(SanicForm):
    login = StringField(label="Почта или юзернейм",
                        render_kw={"placeholder": "invanov@elflesnoy.ru", "autofocus": True},
                        validators=[DataRequired('Поле не может быть пустым')])
    password = PasswordField(label="Пароль", render_kw={"placeholder": "111111"},
                             validators=[DataRequired('Поле не может быть пустым')])


class RegistrationForm(SanicForm):
    username = StringField(label="Юзернейм", render_kw={"placeholder": "elf_lesnoy", "autofocus": True},
                           validators=[DataRequired('Поле не может быть пустым')])
    email = EmailField(label="Почта", render_kw={"placeholder": "invanov@elflesnoy.ru"},
                       validators=[Email('Неправильная почта')])
    password1 = PasswordField(label="Пароль", render_kw={"placeholder": "111111"},
                              validators=[DataRequired('Поле не может быть пустым')])
    password2 = PasswordField(label="Подтверждение пароля", render_kw={"placeholder": "111111"},
                              validators=[EqualTo('password1', 'Пароли не совпадают')])

    photo = FileField(label='Фото вашего лица',
                      render_kw={"onChange": "myFunc(this)", "accept": "image/png, image/jpeg"})
