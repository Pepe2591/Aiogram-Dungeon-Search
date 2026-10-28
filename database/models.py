import os
from datetime import datetime

from dotenv import load_dotenv, find_dotenv
from sqlalchemy import (DateTime, String, func, Integer, BigInteger,
                        SmallInteger, ForeignKey)
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import expression


load_dotenv(find_dotenv(), override=True)

engine = create_async_engine(os.getenv('SQLALHEMY_URL'), echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class User(Base):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)

    profile: Mapped['Profile | None'] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"{self.first_name}, {self.last_name}"


class Profile(Base):
    __tablename__ = "profiles"

    nickname: Mapped[str] = mapped_column(String(30))

    user: Mapped['User'] = relationship(back_populates="profile")
    member: Mapped['Member | None'] = relationship(back_populates="profile")
    admin_role: Mapped['AdminRole | None'] = relationship(back_populates="profiles")

    # unique: на одного пользователя не больше одного профиля
    user_fk: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    admin_role_fk: Mapped[int | None] = mapped_column(
        ForeignKey("admin_roles.id"), nullable=True
    )

    def __repr__(self) -> str:
        return f"{self.id=}, {self.nickname=}, {self.user_fk=}"


class AdminRole(Base):
    """Глобальные админ-роли (не привязаны к клану)."""
    __tablename__ = "admin_roles"

    name: Mapped[str] = mapped_column(String(30), unique=True)
    level_access: Mapped[int] = mapped_column(SmallInteger, unique=True)
    description: Mapped[str] = mapped_column(String(255))

    profiles: Mapped[list['Profile']] = relationship(back_populates="admin_role")

    def __repr__(self) -> str:
        return f"{self.name}, {self.level_access=}, {self.description=}"


class Clan(Base):
    __tablename__ = "clans"

    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # id супергруппы (-100XXXXXXXXXX) занимает 14 символов, берём с запасом
    tg_group_id: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)

    roles: Mapped[list['Role']] = relationship(back_populates="clan")
    members: Mapped[list['Member']] = relationship(back_populates="clan")
    threads: Mapped[list['Thread']] = relationship(back_populates="clan")

    owner_fk: Mapped[int] = mapped_column(ForeignKey("profiles.id"))

    def __repr__(self) -> str:
        return f"{self.id=}, {self.name=}, {self.description=}, {self.tg_group_id=}, {self.owner_fk=}"


class Member(Base):
    __tablename__ = "members"

    is_banned: Mapped[bool] = mapped_column(default=False, server_default=expression.false())
    is_muted: Mapped[bool] = mapped_column(default=False, server_default=expression.false())

    profile: Mapped['Profile'] = relationship(back_populates="member")
    clan: Mapped['Clan'] = relationship(back_populates="members")
    role: Mapped['Role'] = relationship(back_populates="member")
    # у участника может быть много данжей (Dungeon.owner_fk -> members.id)
    dungeons: Mapped[list['Dungeon']] = relationship(back_populates="owner")
    saved_messages: Mapped[list['SavedMessage']] = relationship(back_populates='member')

    # unique: один профиль - один участник клана
    profile_fk: Mapped[int] = mapped_column(ForeignKey("profiles.id"), unique=True)
    clan_fk: Mapped[int] = mapped_column(ForeignKey("clans.id"))
    role_fk: Mapped[int] = mapped_column(ForeignKey('roles.id'))

    def __repr__(self) -> str:
        # не обращаемся к self.profile: в async это вызовет MissingGreenlet
        return f"{self.id=}, {self.profile_fk=}, {self.is_banned=}, {self.is_muted=}"


class Role(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(30))
    level_access: Mapped[int] = mapped_column(SmallInteger)
    description: Mapped[str] = mapped_column(String(255))

    member: Mapped[list['Member']] = relationship(back_populates="role")
    clan: Mapped['Clan'] = relationship(back_populates='roles')

    clan_fk: Mapped[int] = mapped_column(ForeignKey("clans.id"))

    def __repr__(self) -> str:
        return f"{self.name}, {self.level_access=}, {self.description=}"


class Thread(Base):
    __tablename__ = "threads"

    image: Mapped[str] = mapped_column()
    title: Mapped[str] = mapped_column(String(50))
    lvl: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    clan: Mapped['Clan'] = relationship(back_populates="threads")

    clan_id: Mapped[int] = mapped_column(ForeignKey("clans.id"))

    def __repr__(self) -> str:
        return f"{self.title=}, {self.lvl=}, {self.clan_id=}"


class SavedMessage(Base):
    __tablename__ = "saved_messages"

    image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(String(255))

    member: Mapped['Member'] = relationship(back_populates="saved_messages")
    member_fk: Mapped[int] = mapped_column(ForeignKey("members.id"))

    def __repr__(self) -> str:
        return f"{self.member_fk}, {self.content}"


class Dungeon(Base):
    __tablename__ = "dungeons"

    image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lvl: Mapped[int] = mapped_column(SmallInteger)

    # у данжа один владелец
    owner: Mapped['Member'] = relationship(back_populates='dungeons')
    owner_fk: Mapped[int] = mapped_column(ForeignKey("members.id"))

    def __repr__(self) -> str:
        return f"{self.content}, {self.lvl}"


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)