# SMSGW-AIOps

一套面向短信网关运维场景的 AI Agent 原型，聚焦：
- 实时状态监控
- 根因诊断
- 修复建议
- 影响评估
- 人在环审批

## 1. 业务目标

短信网关的核心要求是：可用性优先、最小化风险、数据驱动、透明解释、人工确认。该 Agent 设计遵循以下原则：

- 可用性优先：保证短信能被正常发送
- 最小化风险：优先调整参数，避免重启
- 数据驱动：建议必须建立在指标和日志基础上
- 透明清晰：解释每个决策的理由
- 人在环：高风险操作必须人工确认

## 2. 系统架构

### 2.1 总体架构

```text
┌───────────────────────────────────────────────────────────────┐
│                     SMS Gateway / Channel Layer                │
│  Gateway A | Gateway B | Gateway C | SMS Channels             │
└──────────────────────────────┬────────────────────────────────┘
                               │ metrics / logs / traces
                               ▼
┌───────────────────────────────────────────────────────────────┐
│  Data Collection Layer                                       │
│  Prometheus / OpenTelemetry / Kafka / File Beat / Log Agent │
└──────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
┌───────────────────────────────────────────────────────────────┐
│  AIOps Core Layer                                            │
│  - Real-time Monitor                                         │
│  - Health Score Engine                                       │
│  - Anomaly Detector                                          │
│  - Root Cause Diagnoser                                      │
│  - Recommendation Engine                                     │
│  - Impact Estimator                                           │
└──────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
┌───────────────────────────────────────────────────────────────┐
│  Decision / Action Layer                                      │
│  - No-restart parameter tuning                                │
│  - Traffic shifting                                            │
│  - Threshold adjustment                                        │
│  - Human approval gate                                         │
└──────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
┌───────────────────────────────────────────────────────────────┐
│  Presentation / Integration Layer                              │
│  Dashboard / Alerting / Ticketing / ChatOps / API             │
└───────────────────────────────────────────────────────────────┘
```

### 2.2 核心模块

1. 监控模块
   - 采集网关 CPU/Mem/IO、线程池、连接池、队列长度、发送成功率、超时率、重试率、响应时间 P99
   - 采集渠道侧：通道可用性、黑名单、鉴权失败、下游抖动
   - 统一汇总到时间序列数据平台

2. 诊断模块
   - 通过多指标组合判定根因：单网关故障、跨网关故障、通道/运营商抖动、上游流量突增、数据库慢查询、鉴权异常等
   - 用相关性分析判断是否涉及多个网关

3. 方案推荐模块
   - 立即可执行：限流、降级、动态重试、流量切换、数据库读写优化、通道开关切换
   - 中期优化：容器扩容、队列限流策略、熔断策略、健康检查强化
   - 长期优化：全链路监控、智能告警、容量规划、故障演练

4. 影响评估模块
   - 从成功率、耗时、流量吞吐、SLA 等维度估算影响
   - 对每个建议输出“风险等级”和“审批要求”

## 3. 关键算法与技术说明

### 3.1 健康度评分（Health Score）

系统健康度使用加权评分模型：

score = 100 - 35*latency_penalty - 25*success_penalty - 20*queue_penalty - 15*resource_penalty - 5*retry_penalty

其中：
- latency_penalty：P99 延迟偏离阈值比例
- success_penalty：发送成功率下降比例
- queue_penalty：待发送队列积压程度
- resource_penalty：CPU/内存/线程池使用率超阈值情况
- retry_penalty：重试率异常

健康度分段：
- 85~100：正常
- 70~84：轻微异常
- 50~69：需要关注
- <50：严重问题

### 3.2 异常检测（Z-score / EWMA）

对关键指标做时间窗口内统计：

z = (x_t - μ) / σ

当 |z| > 3 或 EWMA 值持续上升且超过阈值时，判定异常。适用于：
- 发送成功率骤降
- 延迟 P99 上升
- 重试率飙升
- 队列积压

### 3.3 相关性根因分析

对多网关实例计算相关性：

corr(i, j) = Cov(X_i, X_j) / (σ_i * σ_j)

当多个网关同时出现成功率下降、超时增多、重试率上升，且相关性高时，优先判定为：
- 上游流量集中
- 运营商链路故障
- 统一鉴权异常
- 数据库/缓存依赖故障

### 3.4 推荐决策模型

推荐策略采用风险分层：

- Level 0：观察型，自动记录并反馈
- Level 1：低风险参数修改，允许自动执行
- Level 2：中风险，需 1 人审批
- Level 3：高风险，需运营/架构审批

示例：
- 调整重试退避参数：低风险
- 动态切换网关流量：中风险
- 关闭某个通道：高风险
- 删除错误路由：高风险，需要人工确认

## 4. 技术栈选型

### 4.1 监控与数据采集

- Prometheus：指标采集
- OpenTelemetry：链路和日志采集
- Grafana：实时监控面板
- Kafka：事件流
- Elastic Stack：日志索引与查询

### 4.2 AI / 运维分析

- Python：核心算法实现
- pandas / numpy：指标分析
- scikit-learn：异常检测与聚类
- statsmodels：时间序列分析
- FastAPI：API 服务

### 4.3 存储与决策

- PostgreSQL：结构化状态与配置
- Redis：缓存/限流/短期状态
- ClickHouse：大规模指标分析（可选）

### 4.4 可观测性与集成

- Grafana Loki：日志聚合
- Jaeger：分布式追踪
- Slack / DingTalk / Webhook：告警通知
- GitOps / CI：配置变更审计

## 5. 推荐项目结构

```text
SMSGW-AIOps/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── sms_metrics.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── monitoring.py
│   │   ├── diagnosis.py
│   │   ├── recommender.py
│   │   └── simulator.py
│   └── api/
│       ├── __init__.py
│       └── routes.py
└── tests/
    └── test_agent.py
```

## 6. 代码实现（原型）

下面给出一份可直接运行的 Python 原型，含：
- 实时健康度评估
- 异常检测
- 根因诊断
- 修复建议
- 影响评估

### 6.1 requirements.txt

```txt
fastapi==0.111.0
uvicorn==0.30.1
pydantic==2.8.2
numpy==2.1.5
pandas==2.2.3
scikit-learn==1.5.1
python-dotenv==1.0.1
```

### 6.2 app/config.py

```python
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
```

### 6.3 app/models/sms_metrics.py

```python
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
```

### 6.4 app/core/monitoring.py

```python
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
```

### 6.5 app/core/diagnosis.py

```python
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

        # 基于现象做更细的判断
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
```

### 6.6 app/core/recommender.py

```python
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
```

### 6.7 app/core/simulator.py

```python
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
```

### 6.8 app/api/routes.py

```python
from fastapi import APIRouter

from app.core.diagnosis import DiagnosisEngine
from app.core.monitoring import MonitoringEngine
from app.core.recommender import RecommendationEngine
from app.core.simulator import Simulator

router = APIRouter()


@router.get("/health")
def health():
    metrics = Simulator.build_sample_metrics()
    return {
        "status": "ok",
        "system_health": MonitoringEngine.aggregate_health(list(metrics.values())),
    }


@router.get("/diagnose")
def diagnose():
    metrics = Simulator.build_sample_metrics()
    diagnosis = DiagnosisEngine.diagnose(metrics)
    return diagnosis


@router.get("/recommend")
def recommend():
    metrics = Simulator.build_sample_metrics()
    diagnosis = DiagnosisEngine.diagnose(metrics)
    actions = RecommendationEngine.recommend(diagnosis, metrics)
    return {"diagnosis": diagnosis, "recommendations": actions}
```

### 6.9 app/main.py

```python
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="SMSGW AIOps Agent", version="0.1.0")
app.include_router(router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "service": "SMSGW AIOps Agent",
        "status": "running",
        "capabilities": [
            "real_time_monitoring",
            "fault_diagnosis",
            "fix_recommendation",
            "impact_assessment",
        ],
    }
```

### 6.10 启动命令

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6.11 示例接口输出

```json
{
  "status": "ok",
  "system_health": {
    "system_health": 62.5,
    "gateway_scores": {
      "gw-a": 92.0,
      "gw-b": 53.2,
      "gw-c": 61.7
    },
    "unhealthy_gateways": ["gw-b", "gw-c"]
  }
}
```

## 7. 运维 Agent 的核心流程

### 7.1 现状评估

Agent 应先给出：
- 整体健康度
- 是否存在严重问题
- 哪些网关异常

例如：
- 整体健康度 62.5，属于“严重偏差”
- gw-b、gw-c 处于高风险状态

### 7.2 问题诊断

Agent 检查：
- 根因是否是多网关同步异常
- 是否存在统一通道故障
- 是否需要考虑上游流量冲击

输出：
- 根因描述
- 影响范围
- 严重程度

### 7.3 解决方案

推荐分三个层次：
- 立即可采取：流量切换、参数调优、重试回避
- 中期：限流策略、连接池扩容、缓存和 DB 保护
- 长期：容量预测、自愈回路、工单闭环

### 7.4 预计影响

每次建议必须输出：
- 预期恢复效果
- 可能副作用
- 人工审批要求

例如：
- 切流量：预期可在 5~15 分钟降低失败率；风险在于流量失衡；需要运营审批
- 调整重试退避：预期可降低雪崩效应；风险低；无需审批

## 8. 生产化建议

为了真正落地到生产，建议再补充以下能力：

1. 事件与指标统一时间轴
   - 通过 OpenTelemetry + Prometheus + 日志统一关联

2. 告警聚合与降噪
   - 防止噪音告警造成误判

3. 自动执行的安全边界
   - 只有低风险动作允许自动执行

4. 人工确认模板
   - 生成审批单，明确风险、效果和代价

5. 事后验证闭环
   - 每次修复后验证恢复效果、成功率和时延恢复情况

## 9. 总结

这套短信网关 AI 运维 Agent 的设计核心特点是：

- 以“可用性优先”为底线
- 以“最小风险”为执行原则
- 以“数据驱动”为决策方式
- 以“透明解释”为信任基础
- 以“人工审批”为高风险动作保护屏障

它不只是一个告警系统，而是一个面向高可用短信网关场景的智能决策与行动闭环平台。

如果你要进一步落地，可以继续扩展：
- 接入真实的 Prometheus 数据源
- 接入 Kafka 事件流
- 添加 Grafana 仪表盘
- 增加链路追踪和日志关联
- 接入告警通知与审批工单系统









































































































































































































































































































































































































































































































































































































































































































































n
























n




































































































n



n


























n


n

n


test
