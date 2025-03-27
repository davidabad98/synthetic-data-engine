# app/main.py

from fastapi import FastAPI

from app.endpoints import generate

app = FastAPI(
    title="Synthetic Data Engine API",
    description="API for generating synthetic data using prompt engineering and LLMs.",
    version="0.1.0",
)

# Include the generate endpoint router under a common prefix (e.g., /api)
app.include_router(generate.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
