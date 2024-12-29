import os
from typing import List
from sqlalchemy import String
from sqlalchemy.ext.asyncio import create_async_engine

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy.orm import DeclarativeBase

from datetime import datetime, time
from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

engine = create_async_engine(
    os.environ.get(
        "SQL_DATABASE_URL",
        "postgresql+psycopg://bus_bot_admin:test_pass@127.0.0.1:5432/bus_bot",
    )
)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Alert(Base):
    __tablename__ = "alert"

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[str] = mapped_column(String(12))
    atco: Mapped[str] = mapped_column(ForeignKey("stop.atco"))
    line: Mapped[str] = mapped_column(String(18), comment="Bus line")
    alertTime: Mapped[time] = mapped_column(comment="Scheduled alert time")
    weekdays: Mapped[bytes] = mapped_column(
        comment="Bitmap of selected weekdays to run alert on"
    )
    stop: Mapped["Stop"] = relationship(back_populates="alerts")
    lastAlerted: Mapped[datetime] = mapped_column(
        comment="Last time alert was fired", nullable=True
    )


class Stop(Base):
    __tablename__ = "stop"

    atco: Mapped[str] = mapped_column(
        String(18), primary_key=True, comment="ATCO code for bus stop"
    )
    naptan: Mapped[str] = mapped_column(
        String(18), unique=True, comment="NAPTAN code for bus stop"
    )
    name: Mapped[str] = mapped_column(String(120), comment="Full bus stop name")
    alerts: Mapped[List["Alert"]] = relationship(back_populates="stop")


async def sync_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
