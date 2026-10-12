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
