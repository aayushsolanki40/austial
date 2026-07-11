from typing import Optional

from pydantic import BaseModel


class UpdateCatsDto(BaseModel):
    name: Optional[str] = None
