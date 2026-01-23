from fastapi import APIRouter

from app.api.routes import booking, cmd, event, location, login, ticket, users

api_router = APIRouter()
api_router.include_router(cmd.router)
api_router.include_router(users.router)
api_router.include_router(login.router)
api_router.include_router(booking.router)
api_router.include_router(event.router)
api_router.include_router(location.router)
api_router.include_router(ticket.router)
