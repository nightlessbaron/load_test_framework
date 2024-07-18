import asyncio
import aiohttp
import time
from reporter import Reporter
from rate_limiter import RateLimiter
from tqdm import tqdm


class LoadTester:
    """
    Class for performing load testing on a given URL.

    Args:
        url (str): The URL to send requests to.
        qps (int): The number of requests per second to send.
        duration (int): The duration of the load test in seconds.
        concurrency (int): The number of concurrent requests to send.
        timeout (int): The timeout for each request in seconds.
        method (str): The HTTP method to use for the requests.
        headers (dict, optional): The headers to include in the requests. Defaults to None.
        payload (dict, optional): The payload to include in the requests. Defaults to None.
        expected_status (int): The expected HTTP status code for the responses.
        verbose (bool): Whether to print detailed information during the load test.
        output (str): The path to save the load test report.

    Attributes:
        url (str): The URL to send requests to.
        qps (int): The number of requests per second to send.
        duration (int): The duration of the load test in seconds.
        concurrency (int): The number of concurrent requests to send.
        timeout (int): The timeout for each request in seconds.
        method (str): The HTTP method to use for the requests.
        headers (dict): The headers to include in the requests.
        payload (dict): The payload to include in the requests.
        expected_status (int): The expected HTTP status code for the responses.
        verbose (bool): Whether to print detailed information during the load test.
        output (str): The path to save the load test report.
        reporter (Reporter): The reporter object for recording and generating the load test report.
        rate_limiter (RateLimiter): The rate limiter object for controlling the request rate.
        stop_event (asyncio.Event): The event to signal the stop of the load test.
        total_requests (int): The total number of requests to be sent during the load test.

    """

    def __init__(
        self,
        url: str,
        qps: int,
        duration: int,
        concurrency: int,
        timeout: int,
        method: str,
        headers: dict,
        payload: dict,
        expected_status: int,
        verbose: bool,
        output: str,
    ) -> None:
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

    def default_headers(self) -> dict:
        return {"Content-Type": "application/json"}

    def default_payload(self) -> dict:
        return (
            {"example_key": "example_value"} if self.method in ["POST", "PUT"] else None
        )

    async def send_request(
        self, session: aiohttp.ClientSession, progress_bar: tqdm
    ) -> None:
        """
        Sends an HTTP request using the specified session and records the response.

        Args:
            session (aiohttp.ClientSession): The aiohttp client session to use for the request.
            progress_bar (tqdm): The progress bar to update after each request.

        Returns:
            None
        """
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
                        await response.text()
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
                        await response.text()
                        self.reporter.record_response(
                            latency, response.status, self.expected_status
                        )
            except aiohttp.ClientError as e:
                latency = time.time() - start_time
                self.reporter.record_response(latency, None, error=str(e))
            progress_bar.update(1)

    async def run(self) -> None:
        """
        Runs the load test.

        This method creates a client session using aiohttp and sends multiple requests concurrently
        using asyncio tasks. It tracks the progress of the requests using a progress bar and stops
        the test after a specified duration. Finally, it generates a report using the reporter.

        Returns:
            None
        """
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
