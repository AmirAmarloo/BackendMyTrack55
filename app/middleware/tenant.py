from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text
from app.database import SessionLocal

class TenantResolverMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Bypass authentication and documentation endpoints
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/", "/auth/activate"]:
            return await call_next(request)

        tenant_schema = request.headers.get("X-Tenant-ID", "timetracker")
        safe_schema = "".join([c for c in tenant_schema if c.isalnum() or c == "_"])

        db = SessionLocal()
        try:
            db.execute(text(f"SET search_path TO {safe_schema}, timetracker, public"))
            request.state.db = db
            response = await call_next(request)
            return response
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()