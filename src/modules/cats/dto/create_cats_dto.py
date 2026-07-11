from pydantic import BaseModel


class CreateCatsDto(BaseModel):
    name: str
