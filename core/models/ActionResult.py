# core/models/ActionResult.py

from typing import Any
from pydantic import BaseModel, ConfigDict


class ActionResult(BaseModel):
    success: bool
    message: str
    data: Any = None
