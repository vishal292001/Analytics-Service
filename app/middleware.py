import time
import threading
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import os
from dotenv import load_dotenv
load_dotenv() 

# Configuration
RATE_LIMIT = int(os.getenv("RATE_LIMIT"))  # max requests
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW"))  # per IP, in seconds

# In-memory storage for rate-limiting
request_log = {}
lock = threading.Lock()

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        with lock:
            log = request_log.setdefault(client_ip, [])
            # Remove old timestamps outside the window
            request_log[client_ip] = [t for t in log if t > current_time - RATE_LIMIT_WINDOW]

            if len(request_log[client_ip]) >= RATE_LIMIT:
                return JSONResponse(
                    status_code=429,
                    content={
                        "status": 429,
                        "message": "Rate limit exceeded. Try again later."
                    }
                )

            # Allow this request
            request_log[client_ip].append(current_time)

        response = await call_next(request)
        return response
