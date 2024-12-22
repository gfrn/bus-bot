from pydantic import BaseModel, Field, field_validator


class Call(BaseModel):
    """Bus stop call"""

    route_code: str
    time_to_arrival: int | None = Field(alias="display_time")

    @field_validator("time_to_arrival", mode="before")
    def convert_to_int(cls, v: str):
        try:
            return int(v.split()[0])
        except (IndexError, ValueError):
            # This means that the bus is not being tracked, and not set to arrive in the near future.
            return None


class StopUpdate(BaseModel):
    """Bus stop update"""

    calls: list[Call]
