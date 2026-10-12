# Simple test to ensure LangGraph endpoint works (uses simulator + local FAISS KB)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_langgraph_diagnose():
    r = client.get('/api/v1/langgraph/diagnose')
    assert r.status_code == 200
    data = r.json()
    assert 'aggregate' in data
