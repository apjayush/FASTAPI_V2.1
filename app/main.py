from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles  # 👈 add this
import os                                    # 👈 add this

from app.admin import dashboard
from app.auth import auth_router
from app.routers import book_test_ride, messaging, send_brochure, send_list, webhook
from app.mailer import contact as mailer_contact
from app.db import create_pool, close_pool
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.broadcast import broadcast_router, get_templates
from app.template import create_template


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await create_pool()
    yield
    if pool:
        await close_pool(pool)


app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://incoweb.in",
    "http://localhost:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ STATIC MEDIA MOUNT
# BASE_DIR = /home/ayush/Desktop/Project_2.0
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")


# Routers
app.include_router(webhook.router)
app.include_router(send_list.router)
app.include_router(send_brochure.router)
app.include_router(book_test_ride.router)
app.include_router(messaging.router)
app.include_router(auth_router.router)
app.include_router(dashboard.router)
app.include_router(get_templates.router)
app.include_router(broadcast_router.router)
app.include_router(mailer_contact.router)
app.include_router(create_template.router)
