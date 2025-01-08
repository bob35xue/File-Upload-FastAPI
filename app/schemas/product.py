from typing import Optional
from pydantic import BaseModel, Field
from fastapi import Form

class Product(BaseModel):
    name: str = Field(default=Form(None))
    inspector_name: Optional[str] = Field(default=Form(None))
    email: Optional[str] = Field(default=Form(None))
    date_of_inspection: Optional[str] = Field(default=Form(None))
    reason_for_inspection: Optional[str] = Field(default=Form(None))
    station: Optional[str] = Field(default=Form(None))
    unit: Optional[str] = Field(default=Form(None))