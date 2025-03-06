# app/models/request.py

from typing import Dict, Optional

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    input_format: str = Field(..., description="Input format (e.g., CSV, XML, JSON)")
    prompt: str = Field(..., description="User prompt for synthetic data generation")
    volume: int = Field(..., gt=0, description="Number of records to generate")
    parameters: Optional[Dict] = Field(
        None, description="Additional parameters for generation"
    )


class GenerateResponse(BaseModel):
    message: str
    data: dict
