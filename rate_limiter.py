import asyncio


class RateLimiter:
    def __init__(self, rate):
        self.rate = rate
        self.tokens = 0
        self.timestamp = asyncio.get_event_loop().time()
        self.lock = asyncio.Lock()

    async def acquire(self):
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
