import json
import matplotlib.pyplot as plt


class Reporter:
    """
    A class that records and generates reports based on the responses of requests made during load testing.
    """

    def __init__(self) -> None:
        self.latencies = []
        self.errors = 0
        self.total_requests = 0
        self.successful_requests = 0

    def record_response(
        self,
        latency: float,
        status_code: int,
        expected_status: int = None,
        error: Exception = None,
    ) -> None:
        """
        Records the response of a request made during load testing.

        Args:
            latency (float): The latency of the request in seconds.
            status_code (int): The status code of the response.
            expected_status (int, optional): The expected status code. Defaults to None.
            error (Exception, optional): The error that occurred during the request. Defaults to None.
        """
        if error:
            self.errors += 1
        elif status_code == expected_status:
            self.successful_requests += 1
        else:
            self.errors += 1
        self.latencies.append(latency)
        self.total_requests += 1

    def generate_report(self, output: str, verbose: bool) -> None:
        """
        Generates a report based on the collected data.

        Args:
            output (str): The file path to save the report as a JSON file.
            verbose (bool): If True, prints the report to the console.

        Returns:
            None
        """
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        error_rate = self.errors / self.total_requests if self.total_requests else 0
        success_rate = (
            self.successful_requests / self.total_requests if self.total_requests else 0
        )
        percentiles = [50, 90, 95, 99]
        latency_percentiles = {
            f"{p}th_percentile": self.calculate_percentile(p) for p in percentiles
        }

        report = {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "average_latency": avg_latency,
            "error_rate": error_rate,
            "success_rate": success_rate,
            **latency_percentiles,
        }

        if verbose:
            print(json.dumps(report, indent=4))
        if output:
            with open(output, "w") as f:
                json.dump(report, f, indent=4)

        self.generate_graphs()

    def calculate_percentile(self, percentile: float) -> float:
        """
        Calculates the specified percentile of the latencies.

        Args:
            percentile (float): The percentile to calculate. Should be a value between 0 and 100.

        Returns:
            float: The latency value at the specified percentile.

        """
        size = len(self.latencies)
        return sorted(self.latencies)[int(size * percentile / 100) - 1] if size else 0

    def generate_graphs(self) -> None:
        """
        Generates and displays two graphs related to latency.

        The first graph is a histogram showing the distribution of latencies.
        The x-axis represents the latency in seconds, and the y-axis represents the frequency.

        The second graph is a time-series plot showing the latency over time.
        The x-axis represents the request number, and the y-axis represents the latency in seconds.

        The generated graphs are saved as "performance_report.png" and displayed on the screen.
        """
        plt.figure(figsize=(12, 6))

        # Latency Histogram
        plt.subplot(1, 2, 1)
        plt.hist(self.latencies, bins=50, color="blue", alpha=0.7)
        plt.title("Latency Distribution")
        plt.xlabel("Latency (seconds)")
        plt.ylabel("Frequency")

        # Latency Time-series
        plt.subplot(1, 2, 2)
        plt.plot(self.latencies, color="blue", alpha=0.7)
        plt.title("Latency Over Time")
        plt.xlabel("Request Number")
        plt.ylabel("Latency (seconds)")

        plt.tight_layout()
        plt.savefig("performance_report.png")
        plt.show()
