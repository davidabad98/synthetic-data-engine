# app/main.py

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.endpoints import generate

app = FastAPI(
    title="Synthetic Data Engine API",
    description="API for generating synthetic data using prompt engineering and LLMs.",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the generate endpoint router under a common prefix (e.g., /api)
app.include_router(generate.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main_fastapi:app", host="0.0.0.0", port=8000, reload=True)
