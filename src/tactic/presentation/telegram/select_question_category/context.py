from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict

from tactic.domain.entities.category import CategoryDomain
from tactic.presentation.telegram.base_dialog_data import (
    BaseDialogData,
    BaseViewContext,
)


class DialogData(BaseDialogData['DialogData']):
    parent_id: Optional[int] = None
    path: List[str] = field(default_factory=list)
    path_id: List[int] = field(default_factory=list)
    last_questions: List[Dict[str, Any]]  = field(default_factory=list)


class CategoryViewContext(BaseViewContext):
    categories: List[CategoryDomain]
    path: str


class QuestionViewContext(BaseViewContext):
    questions: List[str]
    path: str
    button_indices: List[int]
