"""Simple rate limiting decorator for API calls."""

import time
from functools import wraps
from collections import deque
from threading import Lock
from logger_config import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Simple token bucket rate limiter."""

    def __init__(self, max_calls: int, time_window: float):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()
        self.lock = Lock()

    def __call__(self, func):
        """Decorate a function with rate limiting."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                now = time.time()

                # Remove calls outside the time window
                while self.calls and self.calls[0] < now - self.time_window:
                    self.calls.popleft()

                # Check if we're at the limit
                if len(self.calls) >= self.max_calls:
                    wait_time = self.time_window - (now - self.calls[0])
                    if wait_time > 0:
                        logger.warning(
                            f"Rate limit reached for {func.__name__}, "
                            f"waiting {wait_time:.2f}s"
                        )
                        time.sleep(wait_time)

                        # Clean up again after waiting
                        now = time.time()
                        while self.calls and self.calls[0] < now - self.time_window:
                            self.calls.popleft()

                # Record this call
                self.calls.append(now)

            return func(*args, **kwargs)

        return wrapper


# Pre-configured rate limiters for common use cases

# WandB API: ~60 requests per minute
wandb_rate_limit = RateLimiter(max_calls=60, time_window=60.0)

# Anthropic API: ~50 requests per minute
anthropic_rate_limit = RateLimiter(max_calls=50, time_window=60.0)

# General API: ~100 requests per minute
general_rate_limit = RateLimiter(max_calls=100, time_window=60.0)
