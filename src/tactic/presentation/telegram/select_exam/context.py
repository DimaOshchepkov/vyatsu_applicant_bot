from dataclasses import field
from typing import Dict, List

from tactic.presentation.telegram.base_dialog_data import (
    BaseDialogData,
    BaseViewContext,
)


class ExamDialogData(BaseDialogData["ExamDialogData"]):
    id_to_exam: Dict[int, str] = field(default_factory=dict)
    collected_exams: List[str] = field(default_factory=list)
    last_matches: List[str] = field(default_factory=list)


class MatchItem(BaseViewContext):
    id: int
    title: str


class MatchedExamsContext(BaseViewContext):
    matches: List[MatchItem]
