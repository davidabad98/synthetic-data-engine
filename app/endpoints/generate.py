# app/endpoints/generate.py

from fastapi import APIRouter, HTTPException, status

from app.lambda_function import lambda_handler
from app.models.request import GenerateRequest, GenerateResponse

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
        final_prompt = lambda_handler(request)
        # For the prototype, we simulate an LLM response.
        synthetic_data = {
            "llm_response": final_prompt,
        }

        return GenerateResponse(
            message="Synthetic data generated successfully", data=synthetic_data
        )

    except Exception as e:
        # Log the exception (logging not shown here for brevity)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during synthetic data generation: {str(e)}",
        )
