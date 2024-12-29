from sqlalchemy import and_, delete, or_, select, insert, update
from sqlalchemy.orm import joinedload
from ..models.database import async_session, Alert, Stop
from datetime import datetime, time, timedelta


async def get_alerts(alert_time: time | None = None, user: str | None = None):
    query = select(Alert).options(joinedload(Alert.stop)).order_by(Alert.atco)

    if alert_time is None and user is None:
        raise ValueError("At least one filter must be provided")

    if alert_time:
        # Return alerts within the user-specified time, which haven't been fired in the last 10 minutes
        current_time = datetime.now() - timedelta(minutes=10)
        start_time = time(minute=alert_time.minute - 10, hour=alert_time.hour)
        end_time = time(minute=alert_time.minute + 10, hour=alert_time.hour)

        query = query.filter(
            and_(
                Alert.alertTime > start_time,
                Alert.alertTime < end_time,
                or_(Alert.lastAlerted.is_(None), Alert.lastAlerted < current_time),
            )
        )

    if user:
        query = query.filter(Alert.user == user)

    async with async_session() as session:
        alerts = await session.scalars(query)

    return alerts


async def insert_alert(user: str, naptan: str, alert_time: time, line: str):
    async with async_session() as session:
        atco = await session.scalar(select(Stop.atco).filter(Stop.naptan == naptan))
        if atco is None:
            raise ValueError("Provided bus stop does not exist")
        await session.scalar(
            insert(Alert)
            .returning(Alert)
            .values(
                {
                    "atco": atco,
                    "user": user,
                    "alertTime": alert_time,
                    "line": line,
                    "weekdays": b"f",
                }
            )
        )
        await session.commit()


async def delete_alert(alert_id: int):
    async with async_session() as session:
        affected = await session.execute(delete(Alert).filter(Alert.id == alert_id))
        if affected.rowcount < 1:
            raise ValueError("Provided alert does not exist")

        await session.commit()


async def update_alert(alert_id: int):
    async with async_session() as session:
        await session.execute(
            update(Alert)
            .filter(Alert.id == alert_id)
            .values({"lastAlerted": datetime.now()})
        )
        await session.commit()

