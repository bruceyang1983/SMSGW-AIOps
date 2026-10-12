from dataclasses import dataclass


@dataclass
class AlertThreshold:
    success_rate_min: float = 0.98
    latency_p99_max_ms: float = 800
    queue_depth_max: int = 1000
    retry_rate_max: float = 0.12
    cpu_max: float = 0.8
    memory_max: float = 0.8


THRESHOLD = AlertThreshold()
