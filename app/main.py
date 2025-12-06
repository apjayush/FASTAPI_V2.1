from fastapi import FastAPI
from app.routers import book_test_ride, booking, messaging, send_brochure, send_list, webhook
from app.routers import slots

app = FastAPI()

# include webhook route
app.include_router(webhook.router)
app.include_router(booking.router)
app.include_router(slots.router)
app.include_router(send_list.router)
app.include_router(send_brochure.router)
app.include_router(book_test_ride.router)
app.include_router(messaging.router)