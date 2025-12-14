import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Face Recognition Authentication API using InsightFace",
    version="2.2"
)

# CORS Configuration - Cho phép Frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên set domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])


@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "status": "running",
        "docs_url": "/docs"
    }


if __name__ == "__main__":
    # Reload=True chỉ dùng cho môi trường dev
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
