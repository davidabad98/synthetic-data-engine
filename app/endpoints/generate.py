# app/endpoints/generate.py

import json
import logging
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from app.context.request_context import selected_model_ctx
from app.lambda_function import lambda_handler
from app.models.request import GenerateRequest, GenerateResponse
from config.config import DEFAULT_LLM

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/generate", response_model=GenerateResponse, status_code=status.HTTP_200_OK
)
async def generate_data(request: GenerateRequest):
    """
    Generate synthetic data based on user prompt.
    This endpoint simulates the API Gateway that triggers the processing.
    """
    try:
        logger.info(f"Processing request: {request.model_dump_json()}")

        # Set context for this request chain
        token = selected_model_ctx.set(
            request.parameters.get("selectedModel", DEFAULT_LLM)
        )

        # Call lambda handler and get raw response
        lambda_response = lambda_handler(request, None)

        # Check if lambda returned an error response
        if (
            isinstance(lambda_response, dict)
            and lambda_response.get("statusCode", 200) >= 400
        ):
            error_body = json.loads(lambda_response.get("body", "{}"))
            raise HTTPException(
                status_code=lambda_response["statusCode"],
                detail=error_body.get("error", "Unknown error from lambda handler"),
            )
        else:
            lambda_response = json.loads(lambda_response.get("body", "{}"))

        # If successful, return formatted response
        return GenerateResponse(
            message="Data successfully generated! You can access it here:",
            data=lambda_response,
        )
    except HTTPException:
        raise  # Re-raise our custom HTTP exceptions
    except Exception as e:
        logger.exception(f"Failed to process request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during synthetic data generation: {str(e)}",
        )
    finally:
        # Clean up context to prevent leaks
        selected_model_ctx.reset(token)
