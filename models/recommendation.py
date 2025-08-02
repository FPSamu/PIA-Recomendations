from pydantic import BaseModel
from typing import Literal

class Recommendation(BaseModel):
    title: str
    desc: str
    type: Literal["excessive_expenses", "recurrent_expenses", "savings_opportunities", "no_transactions"]
