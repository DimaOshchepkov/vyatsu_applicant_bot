from typing import Any, Dict, Generic, Hashable, List, Type, TypeVar

from aiogram_dialog import DialogManager
from pydantic import BaseModel

T = TypeVar("T", bound="BaseDialogData")
K = TypeVar("K", bound=Hashable)
V = TypeVar("V", bound=BaseModel)


class BaseDialogData(BaseModel, Generic[T]):
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    def update_manager(self, dialog_manager: DialogManager) -> None:
        dialog_manager.dialog_data.update(self.to_dict())

    @classmethod
    def from_manager(cls: Type[T], manager: DialogManager) -> T:
        return cls.model_validate(manager.dialog_data)

    def _ensure_field_exists(self, field: str):
        if not hasattr(self, field):
            raise AttributeError(f"'{type(self).__name__}' has no field '{field}'")

    def store_model_list(self, field: str, items: List[V]) -> None:
        self._ensure_field_exists(field)
        setattr(self, field, [item.model_dump() for item in items])

    def load_model_list(self, field: str, model_cls: Type[V]) -> List[V]:
        self._ensure_field_exists(field)
        return [model_cls.model_validate(raw) for raw in getattr(self, field, [])]

    def store_model_dict(self, field: str, items: Dict[K, V]) -> None:
        self._ensure_field_exists(field)
        setattr(self, field, {k: v.model_dump() for k, v in items.items()})

    def load_model_dict(self, field: str, model_cls: Type[V]) -> Dict[K, V]:
        self._ensure_field_exists(field)
        raw_dict = getattr(self, field, {})
        return {k: model_cls.model_validate(v) for k, v in raw_dict.items()}


class BaseViewContext(BaseModel):
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
