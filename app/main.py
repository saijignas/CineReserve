"""Main FastAPI application."""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.core.exceptions import MovieReservationException

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    version="1.0.0",
    description="Movie Reservation System API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(MovieReservationException)
async def movie_reservation_exception_handler(
    request: Request, 
    exc: MovieReservationException
) -> JSONResponse:
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "details": str(exc) if settings.DEBUG else None
        }
    )

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "movie-reservation-system"}


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Movie Reservation System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


from app.api.v1 import auth, movies, genres, showtimes, reservations
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Auth"])
app.include_router(movies.router, prefix=f"{settings.API_V1_PREFIX}/movies", tags=["Movies"])
app.include_router(genres.router, prefix=f"{settings.API_V1_PREFIX}/genres", tags=["Genres"])
app.include_router(showtimes.router, prefix=f"{settings.API_V1_PREFIX}/showtimes", tags=["Showtimes"])
app.include_router(reservations.router, prefix=f"{settings.API_V1_PREFIX}/reservations", tags=["Reservations"])
