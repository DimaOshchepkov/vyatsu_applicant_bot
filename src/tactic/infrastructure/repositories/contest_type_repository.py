from aiocache import cached
from tactic.infrastructure.repositories.base_repository import BaseRepository


class ContestTypeRepositoryImpl(
    BaseRepository[ContestTypeDomain, ContestType], ContestTypeRepository
):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ContestTypeDomain, ContestType)


    @cached(ttl=600, key_builder=classaware_key_builder)
    async def get_all(self) -> List[ContestTypeDomain]:
        return await super().get_all()