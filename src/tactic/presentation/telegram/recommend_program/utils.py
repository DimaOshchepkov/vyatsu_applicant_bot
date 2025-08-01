from typing import List, Optional
from aiogram_dialog.widgets.text import Const

def to_id(index: int) -> int:
    return index

def truncate_tail(text: str, max_len: int = 64) -> str:
    return text if len(text) <= max_len else "..." + text[-(max_len - 3) :]

def as_list(value: Optional[int]) -> Optional[List[int]]:
    return [value] if value is not None else None


