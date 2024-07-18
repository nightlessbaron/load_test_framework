import json
import matplotlib.pyplot as plt
import os


class Reporter:
    def __init__(self, output_dir="output"):
        self.latencies = []
        self.errors = 0
        self.total_requests = 0
        self.successful_requests = 0
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def record_response(self, latency, status_code, expected_status=None, error=None):
        if error:
            self.errors += 1
        elif status_code == expected_status:
            self.successful_requests += 1
        else:
            self.errors += 1
        self.latencies.append(latency)
        self.total_requests += 1

    def generate_report(self, output, verbose):
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

    def calculate_percentile(self, percentile):
        size = len(self.latencies)
        return sorted(self.latencies)[int(size * percentile / 100) - 1] if size else 0

    def generate_graphs(self):
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
        plt.savefig(os.path.join(self.output_dir, "performance_report.png"))
        plt.show()
