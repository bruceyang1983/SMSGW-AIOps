from dataclasses import dataclass, asdict


@dataclass
class GateWayMetrics:
    gateway: str
    success_rate: float
    latency_p99_ms: float
    queue_depth: int
    retry_rate: float
    cpu_usage: float
    memory_usage: float
    channel_error_rate: float
    total_sent: int
    total_failed: int

    def to_dict(self):
        return asdict(self)
