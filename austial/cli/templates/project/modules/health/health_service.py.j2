from austial import Injectable
from austial.terminus import HealthCheckService, MemoryHealthIndicator


@Injectable()
class HealthService:
    def __init__(self, health_check_service: HealthCheckService, memory: MemoryHealthIndicator):
        self.health_check_service = health_check_service
        self.memory = memory

    async def check(self) -> dict:
        return await self.health_check_service.check(
            [
                lambda: self.memory.check_heap("memory_heap", 300 * 1024 * 1024),
            ]
        )
