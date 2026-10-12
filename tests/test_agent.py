# tests/test_agent.py

from app.core.diagnosis import DiagnosisEngine
from app.core.monitoring import MonitoringEngine
from app.core.recommender import RecommendationEngine
from app.core.simulator import Simulator


def test_health_score_and_diagnosis():
    metrics = Simulator.build_sample_metrics()
    aggr = MonitoringEngine.aggregate_health(list(metrics.values()))
    diagnosis = DiagnosisEngine.diagnose(metrics)
    decisions = RecommendationEngine.recommend(diagnosis, metrics)

    assert aggr["system_health"] < 100
    assert diagnosis["is_multi_gateway"] is True
    assert len(decisions) >= 3
