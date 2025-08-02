from pydantic import BaseModel
from typing import Literal

class FinancialMovement(BaseModel):
    category: str
    type: Literal["income", "expense"]
    title: str
    account: str
    amount: float
    date: str
