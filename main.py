"""
FastAPI application to fetch random dog images from random.dog API.
"""
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
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


# Sadece izin verilen resim uzantıları
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_RETRIES = 10  # Sonsuz döngüyü önlemek için max deneme sayısı


def is_valid_image_url(url: str) -> bool:
    """URL'in izin verilen bir resim uzantısına sahip olup olmadığını kontrol eder."""
    url_lower = url.lower()
    return any(url_lower.endswith(ext) for ext in ALLOWED_IMAGE_EXTENSIONS)


async def fetch_random_dog() -> DogImageResponse:
    """
    Fetch a random dog IMAGE (not video) from random.dog API.
    Keeps retrying until a valid image URL is returned.

    Returns:
        DogImageResponse: Contains the image URL and file size

    Raises:
        HTTPException: If the external API call fails or max retries exceeded
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.get("https://random.dog/woof.json")
                response.raise_for_status()
                data = response.json()

                url = data["url"]
                file_size = data["fileSizeBytes"]

                # Sadece resim uzantılarını kabul et
                if is_valid_image_url(url):
                    return DogImageResponse(
                        url=url,
                        file_size_bytes=file_size
                    )
                # Video veya desteklenmeyen format -> tekrar dene
                continue

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

        # Max deneme sayısına ulaşıldı
        raise HTTPException(
            status_code=502,
            detail=f"Could not fetch a valid image after {MAX_RETRIES} attempts (random.dog returned videos/unsupported formats)"
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
    response_class=StreamingResponse,
    responses={
        200: {"content": {"image/*": {}}, "description": "Random dog image"},
        502: {"model": ErrorResponse, "description": "Bad gateway - upstream API error"},
        503: {"model": ErrorResponse, "description": "Service unavailable - network error"},
    },
    summary="Get a random dog image (proxied)",
    description="Returns a random dog image directly. URL stays the same, refresh for new image. Use in `<img src=\"...\">` tags.",
)
async def get_random_dog():
    """
    Get a random dog image directly (proxied).

    Returns the actual image content. URL stays as `/dog` — refresh to get a new random dog.
    Perfect for:
    - `<img src="https://your-domain.com/dog" alt="Random Dog" />`
    - Direct browser access — refresh for new image
    - Any client expecting an image response
    """
    dog = await fetch_random_dog()

    # Resmi indir ve stream et
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(dog.url)
            response.raise_for_status()

            # Content-Type header'ını koru
            content_type = response.headers.get("content-type", "image/jpeg")

            return StreamingResponse(
                response.aiter_bytes(chunk_size=8192),
                media_type=content_type,
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                }
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch image: {e.response.status_code}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Network error fetching image: {str(e)}"
            )


@app.get(
    "/dog/json",
    response_model=DogImageResponse,
    responses={
        502: {"model": ErrorResponse, "description": "Bad gateway - upstream API error"},
        503: {"model": ErrorResponse, "description": "Service unavailable - network error"},
    },
    summary="Get random dog image metadata (JSON)",
    description="Returns JSON with image URL and file size. Use when you need the metadata.",
)
async def get_random_dog_json():
    """
    Get random dog image metadata as JSON.

    Returns:
    - **url**: Direct link to the dog image
    - **file_size_bytes**: Size of the image file in bytes
    """
    return await fetch_random_dog()


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