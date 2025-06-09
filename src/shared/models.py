from __future__ import annotations

from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from tactic.domain.value_objects.user import UserId


class Base(DeclarativeBase):
    pass


class ContestType(Base):
    __tablename__ = "contest_type"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    contest_exams: Mapped[list["ProgramContestExam"]] = relationship(
        "ProgramContestExam",
        back_populates="contest_type",
        cascade="all, delete-orphan",
    )


class ScoreStat(Base):
    __tablename__ = "score_stat"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("program.id"), nullable=False)

    stat_type: Mapped[str] = mapped_column(String, nullable=False)  # 'passing' | 'mean'
    budget_places: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    target_places: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    quota_places: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    paid_places: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    program: Mapped["Program"] = relationship("Program", back_populates="score_stats")


class StudyDuration(Base):
    __tablename__ = "study_duration"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    years: Mapped[str] = mapped_column(String, nullable=False)

    programs: Mapped[list[Program]] = relationship(
        "Program", back_populates="study_duration"
    )


class StudyForm(Base):
    __tablename__ = "study_form"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    programs: Mapped[list[Program]] = relationship(
        "Program", back_populates="study_form"
    )
    timeline_bindings: Mapped[list["ProgramTimelineBinding"]] = relationship(
        "ProgramTimelineBinding", back_populates="study_form"
    )


class Program(Base):
    __tablename__ = "program"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    education_level_id: Mapped[int] = mapped_column(
        ForeignKey("education_level.id"), nullable=False
    )
    study_form_id: Mapped[int] = mapped_column(
        ForeignKey("study_form.id"), nullable=False
    )
    study_duration_id: Mapped[int] = mapped_column(
        ForeignKey("study_duration.id"), nullable=False
    )

    program_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    career_info: Mapped[str | None] = mapped_column(Text, nullable=True)

    education_level: Mapped["EducationLevel"] = relationship(
        "EducationLevel", back_populates="programs"
    )
    study_form: Mapped["StudyForm"] = relationship(
        "StudyForm", back_populates="programs"
    )
    study_duration: Mapped["StudyDuration"] = relationship(
        "StudyDuration", back_populates="programs"
    )

    contest_exams: Mapped[list["ProgramContestExam"]] = relationship(
        "ProgramContestExam", back_populates="program", cascade="all, delete-orphan"
    )
    score_stats: Mapped[list["ScoreStat"]] = relationship(
        "ScoreStat", back_populates="program"
    )


class Subject(Base):
    __tablename__ = "subject"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    popularity: Mapped[int] = mapped_column(Integer, nullable=True)

    contest_exams: Mapped[list["ProgramContestExam"]] = relationship(
        "ProgramContestExam", back_populates="subject", cascade="all, delete-orphan"
    )

    aliases: Mapped[list["SubjectAlias"]] = relationship(
        "SubjectAlias", back_populates="subject", cascade="all, delete-orphan"
    )


class ProgramContestExam(Base):
    __tablename__ = "program_contest_exam"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("program.id"), nullable=False)
    contest_type_id: Mapped[int] = mapped_column(
        ForeignKey("contest_type.id"), nullable=False
    )
    subject_id: Mapped[int] = mapped_column(ForeignKey("subject.id"), nullable=False)
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    program: Mapped[Program] = relationship("Program", back_populates="contest_exams")
    contest_type: Mapped[ContestType] = relationship(
        "ContestType", back_populates="contest_exams"
    )
    subject: Mapped[Subject] = relationship("Subject", back_populates="contest_exams")


Index(
    "idx_pce_program_contest",
    ProgramContestExam.program_id,
    ProgramContestExam.contest_type_id,
)


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=False
    )

    category: Mapped["Category"] = relationship("Category", back_populates="questions")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True,
    )

    parent: Mapped[Optional["Category"]] = relationship(
        "Category", remote_side=[id], back_populates="children"
    )

    children: Mapped[List["Category"]] = relationship(
        "Category", back_populates="parent"
    )

    questions: Mapped[List["Question"]] = relationship(
        "Question", back_populates="category"
    )


class TimelineEvent(Base):
    __tablename__ = "timeline_event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    binding_id: Mapped[int] = mapped_column(
        ForeignKey("program_timeline_binding.id"), nullable=False
    )
    name_id: Mapped[int] = mapped_column(
        ForeignKey("timeline_event_name.id"), nullable=False
    )
    deadline: Mapped[Date] = mapped_column(Date, nullable=False)

    binding: Mapped["ProgramTimelineBinding"] = relationship(
        "ProgramTimelineBinding", back_populates="timeline_events"
    )

    event_name: Mapped["TimelineEventName"] = relationship(
        "TimelineEventName", back_populates="events"
    )


class TimelineType(Base):
    __tablename__ = "timeline_type"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    bindings: Mapped[list["ProgramTimelineBinding"]] = relationship(
        "ProgramTimelineBinding", back_populates="type"
    )


class ProgramTimelineBinding(Base):
    __tablename__ = "program_timeline_binding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    education_level_id: Mapped[int] = mapped_column(
        ForeignKey("education_level.id"), nullable=False
    )
    study_form_id: Mapped[int] = mapped_column(
        ForeignKey("study_form.id"), nullable=False
    )
    type_id: Mapped[int] = mapped_column(ForeignKey("timeline_type.id"), nullable=False)

    education_level: Mapped["EducationLevel"] = relationship(
        "EducationLevel", back_populates="timeline_bindings"
    )
    study_form: Mapped["StudyForm"] = relationship(
        "StudyForm", back_populates="timeline_bindings"
    )
    type: Mapped["TimelineType"] = relationship(
        "TimelineType", back_populates="bindings"
    )

    timeline_events: Mapped[list["TimelineEvent"]] = relationship(
        "TimelineEvent", back_populates="binding", cascade="all, delete-orphan"
    )


class EducationLevel(Base):
    __tablename__ = "education_level"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    programs: Mapped[list[Program]] = relationship(
        "Program", back_populates="education_level"
    )
    timeline_bindings: Mapped[list["ProgramTimelineBinding"]] = relationship(
        "ProgramTimelineBinding", back_populates="education_level"
    )


class SubjectAlias(Base):
    __tablename__ = "subject_alias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alias: Mapped[str] = mapped_column(String, unique=False, nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subject.id"), nullable=False)

    subject: Mapped["Subject"] = relationship("Subject", back_populates="aliases")


class TimelineEventName(Base):
    __tablename__ = "timeline_event_name"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    events: Mapped[list["TimelineEvent"]] = relationship(
        "TimelineEvent", back_populates="event_name"
    )


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[UserId] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )
