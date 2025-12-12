from app import app
from logger import logger

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting server on port 80")
    uvicorn.run(app, host="0.0.0.0", port=80)
