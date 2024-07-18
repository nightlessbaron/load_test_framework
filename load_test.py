import asyncio
import aiohttp
import time
from reporter import Reporter
from rate_limiter import RateLimiter
from tqdm import tqdm


class LoadTester:
    def __init__(
        self,
        url,
        qps,
        duration,
        concurrency,
        timeout,
        method,
        headers,
        payload,
        expected_status,
        verbose,
        output,
    ):
        self.url = url
        self.qps = qps
        self.duration = duration
        self.concurrency = concurrency
        self.timeout = timeout
        self.method = method
        self.headers = headers or self.default_headers()
        self.payload = payload or self.default_payload()
        self.expected_status = expected_status
        self.verbose = verbose
        self.output = output
        self.reporter = Reporter()
        self.rate_limiter = RateLimiter(self.qps)
        self.stop_event = asyncio.Event()
        self.total_requests = self.qps * self.duration

    def default_headers(self):
        return {"Content-Type": "application/json"}

    def default_payload(self):
        return (
            {"example_key": "example_value"} if self.method in ["POST", "PUT"] else None
        )

    async def send_request(self, session, progress_bar):
        while not self.stop_event.is_set():
            await self.rate_limiter.acquire()
            start_time = time.time()
            try:
                if self.method in ["POST", "PUT"]:
                    async with session.request(
                        self.method,
                        self.url,
                        headers=self.headers,
                        json=self.payload,
                        timeout=self.timeout,
                    ) as response:
                        latency = time.time() - start_time
                        await response.text()  # Ensure the response is read completely
                        self.reporter.record_response(
                            latency, response.status, self.expected_status
                        )
                else:
                    async with session.request(
                        self.method,
                        self.url,
                        headers=self.headers,
                        timeout=self.timeout,
                    ) as response:
                        latency = time.time() - start_time
                        await response.text()  # Ensure the response is read completely
                        self.reporter.record_response(
                            latency, response.status, self.expected_status
                        )
            except aiohttp.ClientError as e:
                latency = time.time() - start_time
                self.reporter.record_response(latency, None, error=str(e))
            progress_bar.update(1)

    async def run(self):
        async with aiohttp.ClientSession() as session:
            with tqdm(
                total=self.total_requests, desc="Processing requests"
            ) as progress_bar:
                tasks = [
                    asyncio.create_task(self.send_request(session, progress_bar))
                    for _ in range(self.concurrency)
                ]
                await asyncio.sleep(self.duration)
                self.stop_event.set()
                await asyncio.gather(*tasks)

        self.reporter.generate_report(self.output, self.verbose)
