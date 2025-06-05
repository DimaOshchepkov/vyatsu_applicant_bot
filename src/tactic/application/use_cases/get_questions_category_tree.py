from typing import List

from tactic.application.common.repositories import CategoryRepository
from tactic.domain.entities.category_node_model import CategoryNodeModel

    
class GetQuestionsCategoryTreeUseCase:
    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    async def __call__(self) -> List[CategoryNodeModel]:
        return await self.category_repository.get_category_tree()