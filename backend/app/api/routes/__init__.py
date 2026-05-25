from fastapi import APIRouter

from app.auth import auth_routes
from app.api.routes import (
    admin,
    ai,
    downloads,
    edit,
    export_route,
    exports,
    extract,
    health,
    intelligence,
    preview,
    statements,
    system,
    transactions,
    upload,
    versions,
)
from app.api.ws import edit_sync as ws_edit

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(system.router)
api_router.include_router(auth_routes.router)
api_router.include_router(upload.router)
api_router.include_router(statements.router)
api_router.include_router(extract.router)
api_router.include_router(transactions.router)
api_router.include_router(intelligence.router)
api_router.include_router(ai.router)
api_router.include_router(preview.router)
api_router.include_router(edit.router)
api_router.include_router(export_route.router)
api_router.include_router(exports.router)
api_router.include_router(versions.router)
api_router.include_router(downloads.router)
api_router.include_router(admin.router)
api_router.include_router(ws_edit.router)
