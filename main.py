import uvicorn
from src.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8081,
        reload=settings.DEBUG,
        log_level="info",
        log_config=settings.LOGGING,
    )
