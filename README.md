# Load Testing Framework

This is a general-purpose HTTP load-testing and benchmarking library.

## Features

- Support for different HTTP methods (GET, POST, PUT, DELETE).
- Fixed QPS (Queries Per Second).
- Latency and error rate reporting.
- Concurrent requests support.
- Response validation.
- Detailed metrics including percentiles.
- Graphical reports (histograms, time-series charts).
- Asynchronous support.
- Sophisticated rate limiting strategies.
- Progress bar to monitor the testing process.

## Getting Started

### Prerequisites

- Docker
- Git

### Cloning the Repository

```sh
git clone git@github.com:nightlessbaron/load_test_framework.git
cd load_test_framework
```

### Running the Tests

```sh
docker build -t http-load_test .
docker run -it --rm -v "$(pwd)/output:/usr/src/app/output" http-load_test <url> --qps <qps> --duration <dur> --concurrency <con> --timeout <timeout> --method <method> --expected_status <status> --output <output file>
```

An example command:
```sh
docker run -it --rm -v "$(pwd)/output:/usr/src/app/output" http-load_test https://jsonplaceholder.typicode.com/posts/1 --qps 10 --duration 10 --concurrency 10 --timeout 5 --method GET --expected_status 201 --output output/test_report.json
```