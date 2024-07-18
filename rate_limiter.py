import asyncio


class RateLimiter:
    """
    A rate limiter class that limits the rate of acquiring tokens.

    Args:
        rate (float): The rate at which tokens can be acquired per second.

    Attributes:
        rate (float): The rate at which tokens can be acquired per second.
        tokens (float): The number of tokens available.
        timestamp (float): The timestamp of the last token acquisition.
        lock (asyncio.Lock): A lock to ensure thread-safe access to the rate limiter.

    Methods:
        acquire: Acquires a token from the rate limiter.

    """

    def __init__(self, rate: float) -> None:
        self.rate = rate
        self.tokens = 0.0
        self.timestamp = asyncio.get_event_loop().time()
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        """
        Acquires a token from the rate limiter.

        If there are no tokens available, the method will sleep until a token becomes available.

        """
        async with self.lock:
            current_time = asyncio.get_event_loop().time()
            elapsed_time = current_time - self.timestamp
            self.timestamp = current_time
            self.tokens += elapsed_time * self.rate
            if self.tokens > self.rate:
                self.tokens = self.rate

            if self.tokens < 1:
                await asyncio.sleep((1 - self.tokens) / self.rate)
                self.tokens = 0
            else:
                self.tokens -= 1
