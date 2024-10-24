from pydantic import BaseModel, Field
from fastapi import Form

class Product(BaseModel):
    name: str = Field(default=Form(None))