"""
rate_limiter.py
Lightweight in-memory rate limiter (per IP, per endpoint family).
Suitable for single-process deployments. For multi-instance production
deployments, replace with a Redis-backed limiter (e.g. slowapi + Redis).
"""

import time
from collections import defaultdict
from typing import Dict, List

from fastapi import HTTPException, Request, status


class InMemoryRateLimiter:
    def __init__(self, max_requests: int = 20, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: Dict[str, List[float]] = defaultdict(list)

    def check(self, key: str):
        now = time.time()
        window_start = now - self.window_seconds
        hits = self._hits[key]
        # Drop hits outside the window
        hits[:] = [t for t in hits if t > window_start]

        if len(hits) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )
        hits.append(now)


# Stricter limiter for sensitive auth endpoints (login/signup brute force protection)
auth_rate_limiter = InMemoryRateLimiter(max_requests=10, window_seconds=60)
# More lenient limiter for general API endpoints
general_rate_limiter = InMemoryRateLimiter(max_requests=120, window_seconds=60)


def get_client_key(request: Request) -> str:
    """Derive a rate-limit key from the client's IP address."""
    if request.client:
        return request.client.host
    return "unknown"
