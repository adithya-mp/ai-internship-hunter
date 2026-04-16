"""
Rate Limiter Middleware
Protects API endpoints from abuse using SlowAPI.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Create limiter instance
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


def setup_rate_limiter(app):
    """Attach rate limiter to the FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
