from typing import Any, Dict, List, Optional

from pydantic import Field

from tactic.domain.entities.category import CategoryDomain
from tactic.presentation.telegram.base_dialog_data import (
    BaseDialogData,
    BaseViewContext,
)


class DialogData(BaseDialogData['DialogData']):
    parent_id: Optional[int] = None
    path: List[str] = Field(default_factory=list)
    path_id: List[int] = Field(default_factory=list)
    last_questions: List[Dict[str, Any]] = Field(default_factory=list)
    search_results: List[Dict[str, Any]] = Field(default_factory=list)
    search_query: str = Field(default_factory=str)


class CategoryViewContext(BaseViewContext):
    categories: List[CategoryDomain]
    path: str


class QuestionViewContext(BaseViewContext):
    questions: List[str]
    path: str
    button_indices: List[int]
    
    
class QuestionFromVectorDbViewContext(BaseViewContext):
    questions: List[str]
    path: str
    button_indices: List[int]
    search_query: str
