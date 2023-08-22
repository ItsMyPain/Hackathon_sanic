import datetime

from sqlalchemy import func, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, TIMESTAMP, BYTEA, ARRAY, REAL, TEXT, UUID
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(INTEGER, primary_key=True)

    username: Mapped[str] = mapped_column(VARCHAR(150), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(VARCHAR(150), nullable=False, unique=True)
    photo: Mapped[str] = mapped_column(TEXT, nullable=True)

    state_id: Mapped[int] = mapped_column(INTEGER, server_default='1')

    password: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    card: Mapped[str] = mapped_column(VARCHAR(150), nullable=True)
    payment_method_id: Mapped[str] = mapped_column(VARCHAR(150), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, onupdate=func.now(), server_default=func.now())


class Analyze(Base):
    __tablename__ = "analyze"

    user_id: Mapped[int] = mapped_column(ForeignKey(Users.user_id, ondelete='CASCADE', onupdate='CASCADE'),
                                         primary_key=True)

    data: Mapped[list[float]] = mapped_column(ARRAY(REAL), nullable=False)


class Payments(Base):
    __tablename__ = "payments"

    payment_id: Mapped[str] = mapped_column(UUID, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(Users.user_id, ondelete='CASCADE', onupdate='CASCADE'))
    payment_method_id: Mapped[str] = mapped_column(VARCHAR(150), nullable=False, unique=True)

    type_id: Mapped[int] = mapped_column(INTEGER, server_default='1')
    state_id: Mapped[int] = mapped_column(INTEGER, server_default='1')

    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, onupdate=func.now(), server_default=func.now())
