# app/models/request.py
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field, field_validator


class OutputFormat(str, Enum):
    CSV = "csv"
    XML = "xml"
    JSON = "json"
    TEXT = "text"


class GenerateRequest(BaseModel):
    output_format: OutputFormat = Field(
        ..., description="Input format (e.g., CSV, XML, JSON)"
    )
    prompt: str = Field(..., description="User prompt for synthetic data generation")
    volume: int = Field(..., gt=0, description="Number of records to generate")
    parameters: Optional[Dict] = Field(
        None, description="Additional parameters for generation"
    )

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value):
        stripped = value.strip()
        if len(stripped) < 5:
            raise ValueError("Prompt must be at least 5 characters long")
        return stripped


class GenerateResponse(BaseModel):
    message: str
    data: dict
