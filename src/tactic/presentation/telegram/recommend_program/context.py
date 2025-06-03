from dataclasses import field
from typing import Any, Dict, List

from tactic.domain.entities.education_level import EducationLevelDomain
from tactic.domain.entities.study_form import StudyFormDomain
from tactic.presentation.telegram.base_dialog_data import (
    BaseDialogData,
    BaseViewContext,
)
from tactic.presentation.telegram.recommend_program.dto import ProgramResponseEntry


class ExamDialogData(BaseDialogData["ExamDialogData"]):
    id_to_exam: Dict[int, str] = field(default_factory=dict)
    collected_exams: List[str] = field(default_factory=list)
    last_matches: List[str] = field(default_factory=list)
    programs: List[Dict[str, Any]] = field(default_factory=list)


class MatchItem(BaseViewContext):
    id: int
    title: str


class MatchedExamsContext(BaseViewContext):
    matches: List[MatchItem]


class ProgramsContext(BaseViewContext):
    programs: List[ProgramResponseEntry]
    
    
class EducationLevelContext(BaseViewContext):
    education_levels: List[EducationLevelDomain]
    
class StudyFormsContext(BaseViewContext):
    study_forms: List[StudyFormDomain]
