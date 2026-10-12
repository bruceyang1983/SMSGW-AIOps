from fastapi import APIRouter
from typing import Any

from app.core.simulator import Simulator
from app.graph.sms_aiops_graph import LangGraphOrchestrator

router = APIRouter()

@router.get("/langgraph/diagnose")
def lg_diagnose():
    metrics = Simulator.build_sample_metrics()
    orchestrator = LangGraphOrchestrator()
    return orchestrator.run_diagnosis_flow(metrics)
