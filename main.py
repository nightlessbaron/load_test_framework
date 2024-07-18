import argparse
import asyncio
from load_test import LoadTester


def parse_args():
    parser = argparse.ArgumentParser(
        description="HTTP Load Testing and Benchmarking Tool"
    )
    parser.add_argument("url", type=str, help="URL to load test")
    parser.add_argument("--qps", type=int, required=True, help="Queries per second")
    parser.add_argument(
        "--duration", type=int, default=60, help="Duration of the test in seconds"
    )
    parser.add_argument(
        "--concurrency", type=int, default=1, help="Number of concurrent requests"
    )
    parser.add_argument(
        "--timeout", type=int, default=5, help="Timeout for each request in seconds"
    )
    parser.add_argument(
        "--method",
        type=str,
        choices=["GET", "POST", "PUT", "DELETE"],
        default="GET",
        help="HTTP method to use",
    )
    parser.add_argument(
        "--headers", type=str, nargs="*", help="Custom headers in key:value format"
    )
    parser.add_argument(
        "--payload", type=str, help="Request payload for POST/PUT requests"
    )
    parser.add_argument(
        "--expected_status",
        type=int,
        default=200,
        help="Expected status code for validation",
    )
    parser.add_argument("--auth", type=str, help="Authentication token (Bearer)")
    parser.add_argument("--verbose", action="store_false", help="Enable verbose output")
    parser.add_argument(
        "--output", type=str, default="test_report", help="File to save results"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    headers = (
        {k: v for h in args.headers for k, v in (h.split(":"),)} if args.headers else {}
    )
    if args.auth:
        headers["Authorization"] = f"Bearer {args.auth}"
    tester = LoadTester(
        url=args.url,
        qps=args.qps,
        duration=args.duration,
        concurrency=args.concurrency,
        timeout=args.timeout,
        method=args.method,
        headers=headers,
        payload=args.payload,
        expected_status=args.expected_status,
        verbose=args.verbose,
        output=args.output,
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tester.run())


if __name__ == "__main__":
    main()
