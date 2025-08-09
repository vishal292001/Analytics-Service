# main.py
from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from app.router import router
# from app.middleware import RateLimitMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="Analytics Service",
    description="Analytics Service demand forecasts",
    version="1.0.0",
    docs_url='/docs'
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(RateLimitMiddleware)
app.include_router(router)


