from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.tenant import TenantResolverMiddleware
from app.routers import auth

app = FastAPI(
    title="Time Tracking SaaS API",
    version="1.0.0",
    description="Backend API with Schema-per-tenant architecture for German Time-Tracking SaaS"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TenantResolverMiddleware)

app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"status": "online", "message": "Time Tracking API is running with Tenant Resolver"}