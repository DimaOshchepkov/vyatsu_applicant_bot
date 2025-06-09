from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")  # доменная модель
M = TypeVar("M")  # ORM модель


class BaseRepository(Generic[T, M]):
    def __init__(self, db: AsyncSession, domain_model: Type[T], orm_model: Type[M]):
        self.db = db
        self.orm_model = orm_model
        self.domain_model = domain_model

    async def get(self, id: int) -> Optional[T]:
        obj = await self.db.get(self.orm_model, id)
        return self.to_domain(obj) if obj else None

    async def get_all(self) -> List[T]:
        result = await self.db.execute(select(self.orm_model))
        objs = result.scalars().all()
        return [self.to_domain(obj) for obj in objs]

    async def add(self, entity: T) -> T:
        orm_obj = self.to_orm(entity)
        self.db.add(orm_obj)
        await self.db.commit()
        await self.db.refresh(orm_obj)
        return self.to_domain(orm_obj)

    async def update(self, entity: T) -> T:
        orm_obj = self.to_orm(entity)
        await self.db.merge(orm_obj)
        await self.db.commit()
        return self.to_domain(orm_obj)

    async def delete(self, entity: T) -> None:
        orm_obj = self.to_orm(entity)
        await self.db.delete(orm_obj)
        await self.db.commit()

    def to_domain(self, orm_obj: M) -> T:
        data = {k: v for k, v in vars(orm_obj).items() if not k.startswith("_")}
        return self.domain_model(**data)

    def to_orm(self, domain_obj: T) -> M:
        return self.orm_model(**vars(domain_obj))
