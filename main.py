"""
FastAPI application to fetch random dog images from random.dog API.
"""
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional


app = FastAPI(
    title="Get Random Dog API",
    description="A simple API to fetch random dog images from random.dog",
    version="1.0.0",
)


class DogImageResponse(BaseModel):
    """Response model for dog image endpoint."""
    url: str
    file_size_bytes: int


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str


async def fetch_random_dog() -> DogImageResponse:
    """
    Fetch a random dog image from random.dog API.

    Returns:
        DogImageResponse: Contains the image URL and file size

    Raises:
        HTTPException: If the external API call fails
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get("https://random.dog/woof.json")
            response.raise_for_status()
            data = response.json()

            return DogImageResponse(
                url=data["url"],
                file_size_bytes=data["fileSizeBytes"]
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch from random.dog: {e.response.status_code}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Network error when fetching from random.dog: {str(e)}"
            )
        except (KeyError, ValueError) as e:
            raise HTTPException(
                status_code=502,
                detail=f"Invalid response from random.dog: {str(e)}"
            )


@app.get(
    "/",
    response_class=RedirectResponse,
    include_in_schema=False,
)
async def root():
    """Redirect root to the API documentation."""
    return RedirectResponse(url="/docs")


@app.get(
    "/dog",
    response_model=DogImageResponse,
    responses={
        502: {"model": ErrorResponse, "description": "Bad gateway - upstream API error"},
        503: {"model": ErrorResponse, "description": "Service unavailable - network error"},
    },
    summary="Get a random dog image",
    description="Fetches a random dog image URL and its file size from random.dog API",
)
async def get_random_dog():
    """
    Get a random dog image.

    Returns a JSON object with:
    - **url**: Direct link to the dog image (JPG, PNG, GIF, MP4, or WebM)
    - **file_size_bytes**: Size of the image file in bytes
    """
    return await fetch_random_dog()


@app.get(
    "/dog/redirect",
    response_class=RedirectResponse,
    responses={
        502: {"model": ErrorResponse, "description": "Bad gateway - upstream API error"},
        503: {"model": ErrorResponse, "description": "Service unavailable - network error"},
    },
    summary="Redirect to a random dog image",
    description="Redirects directly to a random dog image URL",
)
async def get_random_dog_redirect():
    """
    Redirect to a random dog image directly.

    This endpoint fetches a random dog image and redirects the client
    directly to the image URL. Useful for `<img>` tags or direct linking.
    """
    dog = await fetch_random_dog()
    return RedirectResponse(url=dog.url)


@app.get(
    "/health",
    summary="Health check",
    description="Simple health check endpoint",
)
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "get-random-dog-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)