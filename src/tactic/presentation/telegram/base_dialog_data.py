from dataclasses import asdict, dataclass, field
from typing import Generic, List, Optional, Type, TypeVar

from aiogram_dialog import DialogManager


T = TypeVar("T", bound="BaseDialogData")

@dataclass
class BaseDialogData(Generic[T]):
    def to_dict(self) -> dict:
        return asdict(self)

    def update_manager(self, dialog_manager: "DialogManager") -> None:
        dialog_manager.dialog_data.update(self.to_dict())

    @classmethod
    def from_manager(cls: Type[T], manager: "DialogManager") -> T:
        return cls(**manager.dialog_data)



@dataclass
class BaseViewContext:
    def to_dict(self) -> dict:
        return asdict(self)
