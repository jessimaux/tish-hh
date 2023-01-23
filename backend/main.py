import uvicorn
from fastapi import FastAPI

from app.auth.routers import router as auth_router

app = FastAPI()
app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)