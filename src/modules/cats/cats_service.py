from austial import Injectable, NotFoundException
from src.modules.cats.dto.create_cats_dto import CreateCatsDto
from src.modules.cats.dto.update_cats_dto import UpdateCatsDto
from src.modules.cats.entities.cats_entity import Cats


@Injectable()
class CatsService:
    """In-memory CRUD store -- swap this out for a real repository backed by
    ``austial.database`` (SQLAlchemy) whenever you're ready."""

    def __init__(self):
        self._items: list[Cats] = []
        self._next_id = 1

    def create(self, dto: CreateCatsDto) -> Cats:
        item = Cats(id=self._next_id, **dto.model_dump())
        self._next_id += 1
        self._items.append(item)
        return item

    def find_all(self) -> list[Cats]:
        return self._items

    def find_one(self, id: int) -> Cats:
        for item in self._items:
            if item.id == id:
                return item
        raise NotFoundException(f"Cats #{id} not found")

    def update(self, id: int, dto: UpdateCatsDto) -> Cats:
        item = self.find_one(id)
        updated = item.model_copy(update=dto.model_dump(exclude_unset=True))
        self._items[self._items.index(item)] = updated
        return updated

    def remove(self, id: int) -> None:
        self._items.remove(self.find_one(id))
