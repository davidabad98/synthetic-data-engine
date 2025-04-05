# app/endpoints/generate.py

import json
import logging
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from app.lambda_function import lambda_handler
from app.models.request import GenerateRequest, GenerateResponse

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

        # Call lambda handler and get raw response
        lambda_response = lambda_handler(request)
        # lambda_response = {
        #     "statusCode": 500,
        #     "body": json.dumps({"error": "Custom Error Message"}),
        # }

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
            message="Synthetic data generated successfully", data=lambda_response
        )

    except Exception as e:
        logger.exception(f"Failed to process request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during synthetic data generation: {str(e)}",
        )
