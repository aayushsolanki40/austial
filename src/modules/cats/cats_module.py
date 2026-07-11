from austial import Module

from src.modules.cats.cats_controller import CatsController
from src.modules.cats.cats_service import CatsService


@Module(controllers=[CatsController], providers=[CatsService])
class CatsModule:
    pass
