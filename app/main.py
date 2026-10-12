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
