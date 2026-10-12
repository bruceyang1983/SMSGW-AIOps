from collections import defaultdict


class DiagnosisEngine:
    @staticmethod
    def diagnose(metrics_by_gateway: dict) -> dict:
        findings = []
        failed_gateways = []

        for gateway, metrics in metrics_by_gateway.items():
            if metrics.success_rate < 0.98 or metrics.channel_error_rate > 0.05:
                failed_gateways.append(gateway)

        if len(failed_gateways) == 0:
            root_cause = "系统整体正常，未发现明显故障"
            severity = "info"
        elif len(failed_gateways) == 1:
            root_cause = f"单网关异常，优先检查 {failed_gateways[0]} 的通道、连接池和资源占用"
            severity = "warning"
        else:
            root_cause = "多个网关同步异常，优先怀疑上游通道、统一鉴权、缓存/DB 或大规模流量冲击"
            severity = "critical"

        for gateway, metrics in metrics_by_gateway.items():
            if metrics.retry_rate > 0.12 and metrics.queue_depth > 800:
                findings.append(f"{gateway}: 重试飙升 + 队列积压，可能存在上游回压或通道响应变慢")
            if metrics.channel_error_rate > 0.05:
                findings.append(f"{gateway}: 通道错误率高，可能涉及运营商或渠道鉴权问题")
            if metrics.cpu_usage > 0.8 or metrics.memory_usage > 0.8:
                findings.append(f"{gateway}: 资源过载，可能出现线程池和内存压力")

        return {
            "root_cause": root_cause,
            "severity": severity,
            "affected_gateways": failed_gateways,
            "evidence": findings,
            "is_multi_gateway": len(failed_gateways) > 1,
        }
