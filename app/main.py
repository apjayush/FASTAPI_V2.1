from fastapi import FastAPI
from app.routers import book_test_ride, messaging, send_brochure, send_list, webhook, auth
from app.db import create_pool, close_pool
from contextlib import asynccontextmanager

# app = FastAPI()



# Define lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await create_pool()  # Assign to global pool
    yield
    if pool:
        await close_pool(pool)

app = FastAPI(lifespan=lifespan)  # Single app instance with lifespan


# include webhook route
app.include_router(webhook.router)
app.include_router(send_list.router)
app.include_router(send_brochure.router)
app.include_router(book_test_ride.router)
app.include_router(messaging.router)
app.include_router(auth.router)