from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import settings

from apps.core.routers import router as core_router
from apps.auth.routers import router as auth_router
from apps.events.routers import router as events_router
from apps.admin.routers import router as admin_router
from apps.users.routers import router as users_router
from apps.feed.routers import router as feed_router
from apps.search.routers import router as search_router


app = FastAPI()

# routers
app.include_router(core_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(events_router)
app.include_router(feed_router)
app.include_router(search_router)
app.include_router(admin_router, prefix="/admin", tags=['admin'])

# Static files
app.mount("/media", StaticFiles(directory=settings.MEDIADIR), name="media")

# CORS section
origins = [
    'http://localhost',
    'http://127.0.0.1',
    'http://localhost:8100',
    'http://127.0.0.1:8100',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
