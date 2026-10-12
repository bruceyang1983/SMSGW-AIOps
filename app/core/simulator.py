from app.models.sms_metrics import GateWayMetrics


class Simulator:
    @staticmethod
    def build_sample_metrics() -> dict:
        return {
            "gw-a": GateWayMetrics(
                gateway="gw-a",
                success_rate=0.995,
                latency_p99_ms=430,
                queue_depth=200,
                retry_rate=0.06,
                cpu_usage=0.62,
                memory_usage=0.58,
                channel_error_rate=0.02,
                total_sent=120000,
                total_failed=600,
            ),
            "gw-b": GateWayMetrics(
                gateway="gw-b",
                success_rate=0.96,
                latency_p99_ms=1200,
                queue_depth=1500,
                retry_rate=0.16,
                cpu_usage=0.89,
                memory_usage=0.76,
                channel_error_rate=0.08,
                total_sent=98000,
                total_failed=3900,
            ),
            "gw-c": GateWayMetrics(
                gateway="gw-c",
                success_rate=0.97,
                latency_p99_ms=900,
                queue_depth=1000,
                retry_rate=0.14,
                cpu_usage=0.8,
                memory_usage=0.7,
                channel_error_rate=0.06,
                total_sent=110000,
                total_failed=3300,
            ),
        }
