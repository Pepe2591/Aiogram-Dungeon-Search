from datetime import datetime

from sqlalchemy import DateTime, String, func, Integer, BigInteger, SmallInteger, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv(), override=True)

engine = create_async_engine(os.getenv('SQLALHEMY_URL'), echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class User(Base):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    profile : Mapped['Profile'] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"{self.first_name}, {self.last_name}"


class Profile(Base):
    __tablename__ = "profiles"

    nickname : Mapped[str] = mapped_column(String(30))
    admin_rank : Mapped[int] = mapped_column()

    user : Mapped['User'] = relationship(back_populates="profile")
    member : Mapped['Member'] = relationship(back_populates="profile")

    user_fk: Mapped[int] = mapped_column(ForeignKey("users.id"))

    def __repr__(self) -> str:
        return f"{self.id=}, {self.nickname=}, {self.user_fk=}"


class Clan(Base):
    __tablename__ = "clans"

    name : Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    tg_group_id : Mapped[str] = mapped_column(String(14), unique=True, nullable=True)

    roles : Mapped[list['Role']] = relationship(back_populates="clan")
    members : Mapped[list['Member']] = relationship(back_populates="clan")
    threads : Mapped[list['Thread']] = relationship(back_populates="clan")

    owner_fk : Mapped[int] = mapped_column(ForeignKey("profiles.id"))

    def __repr__(self) -> str:
        return f"{self.id=}, {self.name=}, {self.description=}, {self.tg_group_id=}, {self.owner_fk=}"



class Member(Base):
    __tablename__ = "members"

    is_banned : Mapped[bool] = mapped_column()
    is_muted : Mapped[bool] = mapped_column()

    profile : Mapped['Profile'] = relationship(back_populates="member")
    clan : Mapped['Clan'] = relationship(back_populates="members")
    role : Mapped['Role'] = relationship(back_populates="member")
    dungeons: Mapped['Dungeon'] = relationship(back_populates="members")
    saved_messages : Mapped[list['SavedMessage']] = relationship(back_populates='member')

    profile_fk: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    clan_fk : Mapped[int] = mapped_column(ForeignKey("clans.id"))
    role_fk : Mapped[int] = mapped_column(ForeignKey('roles.id'))


    def __repr__(self) -> str:
        return f"{self.profile.nickname=}, {self.is_banned=}, {self.is_muted=}"

class Role(Base):
    __tablename__ = "roles"

    name : Mapped[str] = mapped_column(String(30))
    level_access: Mapped[int] = mapped_column(SmallInteger)
    description : Mapped[str] = mapped_column(String(255))

    member : Mapped[list['Member']] = relationship(back_populates="role")
    clan : Mapped['Clan'] = relationship(back_populates='roles')

    clan_fk : Mapped[int] = mapped_column(ForeignKey("clans.id"))

    def __repr__(self) -> str:
        return f"{self.name}, {self.level_access=}, {self.description=}"


class Thread(Base):
    __tablename__ = "threads"

    image : Mapped[str] = mapped_column()
    title : Mapped[str] = mapped_column(String(50))
    lvl : Mapped[int] = mapped_column(SmallInteger, nullable=True)

    clan : Mapped['Clan'] = relationship(back_populates="threads")

    clan_id : Mapped[int] = mapped_column(ForeignKey("clans.id"))

    def __repr__(self) -> str:
        return f"{self.title=}, {self.lvl=}, {self.clan_id=}"


class SavedMessage(Base):
    __tablename__ = "saved_messages"

    image : Mapped[str] = mapped_column(String(255), nullable=True)
    content : Mapped[str] = mapped_column(String(255))

    member : Mapped['Member'] = relationship(back_populates="saved_messages")
    member_fk : Mapped[int] = mapped_column(ForeignKey("members.id"))

    def __repr__(self) -> str:
        return f"{self.member_fk}, {self.content}"


class Dungeon(Base):
    __tablename__ = "dungeons"

    image : Mapped[str | None] = mapped_column(String(255), nullable=True)
    content : Mapped[str] = mapped_column(String(255), nullable=True)
    lvl : Mapped[int] = mapped_column(SmallInteger)

    members : Mapped[list['Member']] = relationship(back_populates='dungeons')
    owner_fk : Mapped[int] = mapped_column(ForeignKey("members.id"))

    def __repr__(self) -> str:
        return f"{self.content, self.lvl}"

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)