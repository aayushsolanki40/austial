from austial import Body, Controller, Delete, Get, Patch, Post
from src.modules.cats.cats_service import CatsService
from src.modules.cats.dto.create_cats_dto import CreateCatsDto
from src.modules.cats.dto.update_cats_dto import UpdateCatsDto
from src.modules.cats.entities.cats_entity import Cats


@Controller("cats")
class CatsController:
    def __init__(self, service: CatsService):
        self.service = service

    @Post()
    async def create(self, dto: CreateCatsDto = Body()) -> Cats:
        return self.service.create(dto)

    @Get()
    async def find_all(self) -> list[Cats]:
        return self.service.find_all()

    @Get(":id")
    async def find_one(self, id: int) -> Cats:
        return self.service.find_one(id)

    @Patch(":id")
    async def update(self, id: int, dto: UpdateCatsDto = Body()) -> Cats:
        return self.service.update(id, dto)

    @Delete(":id")
    async def remove(self, id: int) -> dict:
        self.service.remove(id)
        return {"deleted": True}
