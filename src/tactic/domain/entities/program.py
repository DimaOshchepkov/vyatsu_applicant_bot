from typing import Optional

from pydantic import BaseModel


class ProgramDomain(BaseModel):
    id: int
    title: str
    url: str
    education_level_id: int
    study_form_id: int
    study_duration_id: int
    program_info: Optional[str]
    career_info: Optional[str]
