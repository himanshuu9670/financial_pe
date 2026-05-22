from fastapi import APIRouter

from app.api.routes import edit, export_route, extract, health, preview, statements, transactions, upload

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(upload.router)
api_router.include_router(statements.router)
api_router.include_router(extract.router)
api_router.include_router(transactions.router)
api_router.include_router(preview.router)
api_router.include_router(edit.router)
api_router.include_router(export_route.router)
