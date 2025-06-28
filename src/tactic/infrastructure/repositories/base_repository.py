from typing import Collection, Generic, List, Optional, Sequence, Type, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import HaveAutoincriment

T = TypeVar("T")  # доменная модель
M = TypeVar("M", bound=HaveAutoincriment)  # ORM модель
TCreate = TypeVar("TCreate")  # DTO для создания


class BaseRepository(Generic[T, M, TCreate]):
    def __init__(
        self,
        db: AsyncSession,
        domain_model: Type[T],
        orm_model: Type[M],
        create_model: Type[TCreate],
    ):
        self.db = db
        self.orm_model = orm_model
        self.domain_model = domain_model
        self.create_model = create_model

    async def get(self, id: int) -> Optional[T]:
        obj = await self.db.get(self.orm_model, id)
        return self.to_domain(obj) if obj else None

    async def get_all(self) -> List[T]:
        result = await self.db.execute(select(self.orm_model))
        objs = result.scalars().all()
        return [self.to_domain(obj) for obj in objs]
    
    async def get_many(self, ids: Collection[int]) -> List[T]:
        if not ids:
            return []

        stmt = select(self.orm_model).where(self.orm_model.id.in_(ids))
        result = await self.db.execute(stmt)
        objs = result.scalars().all()
        return [self.to_domain(obj) for obj in objs]

    async def add(self, create_dto: TCreate) -> T:
        orm_obj = self.to_orm_from_create(create_dto)
        self.db.add(orm_obj)
        await self.db.flush()
        return self.to_domain(orm_obj)

    async def add_all(self, create_dtos: Sequence[TCreate]) -> List[T]:
        orm_objs = [self.to_orm_from_create(dto) for dto in create_dtos]
        self.db.add_all(orm_objs)
        await self.db.flush()
        ids = [obj.id for obj in orm_objs]
        return await self.get_many(ids)

    async def update(self, entity: T) -> T:
        orm_obj = await self.db.merge(self.to_orm(entity))
        return self.to_domain(orm_obj)

    async def delete(self, id: int) -> None:
        stmt = delete(self.orm_model).where(self.orm_model.id == id)
        await self.db.execute(stmt)
        await self.db.flush() 
            
    async def delete_all(self, ids: List[int]) -> None:
        if not ids:
            return
        stmt = delete(self.orm_model).where(self.orm_model.id.in_(ids))
        await self.db.execute(stmt)
        await self.db.flush()

    def to_domain(self, orm_obj: M) -> T:
        data = {k: v for k, v in vars(orm_obj).items() if not k.startswith("_")}
        return self.domain_model(**data)

    def to_orm(self, domain_obj: T) -> M:
        return self.orm_model(**vars(domain_obj))

    def to_orm_from_create(self, create_dto: TCreate) -> M:
        data = vars(create_dto)
        return self.orm_model(**data)
