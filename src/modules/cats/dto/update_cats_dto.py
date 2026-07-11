from pydantic import BaseModel


class UpdateCatsDto(BaseModel):
    name: str | None = None
