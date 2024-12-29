
import os
from typing import List

import aiohttp
from sqlalchemy import func, select

from ..models.database import Stop
from ..models.database import async_session

ATCO_PREFIX = os.environ.get("ATCO_PREFIX", "340")

async def populate_stops():
    """Get all bus stops, parse data, and push to database"""

    async with async_session() as session:
        # Do not overwrite existing stops if already in database
        stop_count = await session.scalar(select(func.count(Stop.atco)))

        if stop_count is not None and stop_count > 0:
            # TODO: log when this happens
            return
    
    stops: List[Stop] = []
    async with aiohttp.ClientSession() as http_session:
        async with http_session.get(
                f"https://naptan.api.dft.gov.uk/v1/access-nodes?dataFormat=csv&atcoAreaCodes={ATCO_PREFIX}"
            ) as resp:
                resp_csv = await resp.text()
    
    resp_rows = [row.split(",") for row in resp_csv.split("\n")[1:]]

    for row in resp_rows:
        if len(row) == 43 and row[42] == "active" and row[1] != "":
            stops.append(Stop(atco=row[0], naptan=row[1], name=row[4]))
    
    async with async_session() as session:
        session.add_all(stops)
        await session.commit()
                
    