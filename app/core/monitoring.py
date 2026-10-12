import math
from typing import List

from app.config import THRESHOLD
from app.models.sms_metrics import GateWayMetrics


class MonitoringEngine:
    @staticmethod
    def health_score(metrics: GateWayMetrics) -> float:
        latency_penalty = max(0.0, (metrics.latency_p99_ms - THRESHOLD.latency_p99_max_ms) / THRESHOLD.latency_p99_max_ms)
        success_penalty = max(0.0, (THRESHOLD.success_rate_min - metrics.success_rate) / THRESHOLD.success_rate_min)
        queue_penalty = max(0.0, (metrics.queue_depth - THRESHOLD.queue_depth_max) / THRESHOLD.queue_depth_max)
        cpu_penalty = max(0.0, (metrics.cpu_usage - THRESHOLD.cpu_max) / THRESHOLD.cpu_max)
        memory_penalty = max(0.0, (metrics.memory_usage - THRESHOLD.memory_max) / THRESHOLD.memory_max)
        retry_penalty = max(0.0, (metrics.retry_rate - THRESHOLD.retry_rate_max) / THRESHOLD.retry_rate_max)

        score = 100.0
        score -= 35.0 * latency_penalty
        score -= 25.0 * success_penalty
        score -= 20.0 * queue_penalty
        score -= 15.0 * (max(cpu_penalty, memory_penalty))
        score -= 5.0 * retry_penalty
        return round(max(0.0, min(score, 100.0)), 2)

    @staticmethod
    def detect_anomaly(metrics: GateWayMetrics) -> dict:
        issues = []
        if metrics.success_rate < THRESHOLD.success_rate_min:
            issues.append("发送成功率低于阈值")
        if metrics.latency_p99_ms > THRESHOLD.latency_p99_max_ms:
            issues.append("P99 延迟异常")
        if metrics.queue_depth > THRESHOLD.queue_depth_max:
            issues.append("待发送队列积压")
        if metrics.retry_rate > THRESHOLD.retry_rate_max:
            issues.append("重试率异常")
        if metrics.cpu_usage > THRESHOLD.cpu_max or metrics.memory_usage > THRESHOLD.memory_max:
            issues.append("资源占用过高")
        if metrics.channel_error_rate > 0.05:
            issues.append("通道错误率上升")

        return {
            "has_anomaly": bool(issues),
            "issues": issues,
            "severity": "critical" if len(issues) >= 4 else "warning" if len(issues) >= 2 else "info",
        }

    @staticmethod
    def aggregate_health(metrics_list: List[GateWayMetrics]) -> dict:
        scores = [MonitoringEngine.health_score(x) for x in metrics_list]
        avg_score = sum(scores) / len(scores) if scores else 0

        return {
            "system_health": round(avg_score, 2),
            "gateway_scores": {m.gateway: MonitoringEngine.health_score(m) for m in metrics_list},
            "unhealthy_gateways": [m.gateway for m in metrics_list if MonitoringEngine.health_score(m) < 70],
        }
