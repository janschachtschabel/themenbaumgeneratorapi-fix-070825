from pydantic import BaseModel, Field


class Ping(BaseModel):
    status: str = Field(
        default="ok",
        description="Ping response of the server. Should be 'ok' in happy-case.",
        examples=["ok", "not ok"],
    )
