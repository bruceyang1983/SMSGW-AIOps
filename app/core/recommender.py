from typing import List, Dict


class RecommendationEngine:
    @staticmethod
    def recommend(diagnosis: dict, metrics_by_gateway: dict) -> List[Dict]:
        actions = []

        if diagnosis["is_multi_gateway"]:
            actions.append({
                "priority": "P1",
                "title": "临时分流流量至健康网关",
                "action": "在不重启服务的前提下，将部分短信流量切到可用网关，避免单点拥塞",
                "risk": "medium",
                "approval_required": True,
                "impact": "可降低短时失败率并保护核心发送链路",
            })

            actions.append({
                "priority": "P1",
                "title": "调高重试退避参数并限制瞬时并发",
                "action": "减少毁灭性重试造成的雪崩效应，同时保护下游通道",
                "risk": "low",
                "approval_required": False,
                "impact": "可平缓抖动，降低峰值压力",
            })
        else:
            actions.append({
                "priority": "P1",
                "title": "检查单网关通道状态和鉴权配置",
                "action": "先用指标和日志确认是否为单通道故障或网关配置异常",
                "risk": "low",
                "approval_required": False,
                "impact": "通常能在最短时间恢复单网关稳定性",
            })

        actions.append({
            "priority": "P2",
            "title": "中期优化：扩大连接池/线程池冗余和限流策略",
            "action": "通过自动扩容或参数调优减少负载冲击",
            "risk": "medium",
            "approval_required": True,
            "impact": "提升峰值承载能力和整体稳定性",
        })

        actions.append({
            "priority": "P3",
            "title": "长期优化：建立 AI 告警与容量预测",
            "action": "引入时间序列预测、通道健康评分和可视化告警联动机制",
            "risk": "low",
            "approval_required": False,
            "impact": "降低未来故障发生率和运维成本",
        })

        return actions
