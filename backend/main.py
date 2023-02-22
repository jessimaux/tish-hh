from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps.auth.routers import router as auth_router
from apps.events.routers import router as events_router
from apps.admin.routers import router as admin_router
from apps.users.routers import router as users_router
from apps.feed.routers import router as feed_router
from apps.search.routers import router as search_router
import settings

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(events_router)
app.include_router(feed_router)
app.include_router(search_router)
app.include_router(admin_router, prefix="/admin", tags=['admin'])

app.mount("/media", StaticFiles(directory=settings.MEDIADIR), name="media")