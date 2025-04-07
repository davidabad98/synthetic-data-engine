# app/endpoints/upload.py

import json
import logging
import os

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.context.request_context import selected_model_ctx
from app.lambda_function import lambda_handler
from app.models.request import GenerateResponse
from app.upload_main import main
from app.utils.utility import save_uploaded_data_locally, save_uploaded_data_to_s3
from config.config import ALLOWED_UPLOAD_EXTENSIONS, SAVE_UPLOADED_FILE, SERVER_MODE

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...), selected_model: str = Form(..., alias="selectedModel")
):
    try:

        # Set context for this request chain
        token = selected_model_ctx.set(selected_model)

        # --- Validation 1: Check file extension ---
        file_extension = (
            os.path.splitext(file.filename)[1].lower() if file.filename else ""
        )
        if file_extension not in ALLOWED_UPLOAD_EXTENSIONS:
            error = f"Invalid file type. Only {', '.join(ALLOWED_UPLOAD_EXTENSIONS)} files are allowed"
            logger.error(error)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

        # --- Read content ---
        content = await file.read()

        # --- Save uploaded file ---
        if SAVE_UPLOADED_FILE:
            if SERVER_MODE == "local":
                upload_result = await save_uploaded_data_locally(file, content)
            else:
                upload_result = await save_uploaded_data_to_s3(file, content)

        # Call lambda handler and get raw response
        lambda_response = lambda_handler(None, content)

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

    except HTTPException:
        raise  # Re-raise our custom HTTP exceptions
    except Exception as e:
        logger.exception(f"Failed to process request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}",
        )
    finally:
        # Clean up context to prevent leaks
        selected_model_ctx.reset(token)
