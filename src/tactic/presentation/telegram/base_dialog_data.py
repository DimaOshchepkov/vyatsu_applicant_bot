from typing import Any, Dict, Generic, Type, TypeVar

from aiogram_dialog import DialogManager
from pydantic import BaseModel

T = TypeVar("T", bound="BaseDialogData")


class BaseDialogData(BaseModel, Generic[T]):

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    def update_manager(self, dialog_manager: DialogManager) -> None:
        dialog_manager.dialog_data.update(self.to_dict())

    @classmethod
    def from_manager(cls: Type[T], manager: DialogManager) -> T:
        return cls.model_validate(manager.dialog_data)


class BaseViewContext(BaseModel):
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
