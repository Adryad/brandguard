from fastapi import FastAPI
from fastapi.responses import JSONResponse
import asyncpg
import redis
import os

app = FastAPI(title="BrandGuard API")


# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Check database connection
        db_url = os.getenv(
            "DATABASE_URL",
            "postgresql://brandguard:brandguard123@postgres:5432/brandguard",
        )
        conn = await asyncpg.connect(db_url)
        await conn.close()

        # Check Redis connection
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        r = redis.from_url(redis_url)
        r.ping()

        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "database": "connected",
                "redis": "connected",
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=503, content={"status": "unhealthy", "error": str(e)}
        )


@app.get("/")
async def root():
    return {"message": "BrandGuard API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
