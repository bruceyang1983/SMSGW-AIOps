from fastapi import FastAPI
from app.api.routes import router as core_router
from app.api.langgraph_routes import router as lg_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="SMSGW AIOps LangGraph RAG Demo")
app.include_router(core_router, prefix="/api/v1")
app.include_router(lg_router, prefix="/api/v1")

# serve stub frontend
app.mount("/ui", StaticFiles(directory="app/frontend/copilotkit_stub"), name="ui")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
