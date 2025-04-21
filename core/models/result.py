# core/models/result.py

from typing import Any
from pydantic import BaseModel


class ActionResult(BaseModel):
    success: bool
    message: str
    data: Any = None
