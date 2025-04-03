# app/models/request.py
import random
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
            error_messages = [
                "📝 Let's try that again! Your request needs to be at least 5 characters to work with. Could you please add a bit more detail?\nExample: '5 customer records for a dental insurance policy'",
                "🤖 Almost there! Please give me a slightly longer description (at least 5 characters) so I can create the best data for you!",
                "✨ Data generation needs fuel! Please provide a prompt of at least 5 characters to get started.",
                "📦 Let's build something great! Could you expand your request to 5+ characters? Example: '10 entries for a fhsa investment.'",
            ]
            raise ValueError(random.choice(error_messages))
        return stripped


class GenerateResponse(BaseModel):
    message: str
    data: dict
