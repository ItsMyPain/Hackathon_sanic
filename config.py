from sanic import Sanic


class TextColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def pprint(print_data: object, color: str = TextColors.OKGREEN):
    print(f'{color}{print_data}{TextColors.ENDC}')


def load_config(app: Sanic):
    if app.debug:
        pprint('Окружение: development')

    else:
        pprint('Окружение: production')

    # app.config.SMTP_EMAIL = os.getenv('SMTP_EMAIL')
    # app.config.SMTP_PSWD = os.getenv('SMTP_PSWD')
    # app.config.SMTP_HOST = os.getenv('SMTP_HOST')
    # app.config.SMTP_PORT = os.getenv('SMTP_PORT')

    app.config.SECRET_KEY = 'pupa'
    app.config.HTTPONLY_COOKIES = True
    app.config.SECURE_COOKIES = True
    app.config.TOKEN_TIME = 60 * 60

    pprint('Окружение загружено')
