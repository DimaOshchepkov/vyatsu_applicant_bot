from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from tactic.domain.entities.contest_type import ContestTypeDomain
from tactic.domain.entities.education_level import EducationLevelDomain
from tactic.domain.entities.study_form import StudyFormDomain
from tactic.presentation.telegram.base_dialog_data import (
    BaseDialogData,
    BaseViewContext,
)
from tactic.presentation.telegram.recommend_program.dto import ProgramResponseEntry


class ExamDialogData(BaseDialogData["ExamDialogData"]):
    id_to_subject: Dict[int, Dict[str, Any]] = Field(default_factory=dict)
    collected_subjects: Dict[int, Dict[str, Any]] = Field(default_factory=dict)
    programs: List[Dict[str, Any]] = Field(default_factory=list)
    education_level_id: Optional[int] = None
    study_form_id: Optional[int] = None
    contest_type_id: Optional[int] = None

    class FIELDS(Enum):
        ID_TO_SUBJECT = "id_to_subject"
        COLLECTED_SUBJECTS = "collected_subjects"
        PROGRAMS = "programs"
        EDUCATION_LEVEL_ID = "education_level_id"
        STUDY_FORM_ID = "study_form_id"
        CONTEST_TYPE_ID = "contest_type_id"


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


class ContestTypesContext(BaseViewContext):
    contest_types: List[ContestTypeDomain]
