from pydantic import BaseModel


class Cats(BaseModel):
    id: int
    name: str
