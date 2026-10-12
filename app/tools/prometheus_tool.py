from typing import Optional
import os
import requests

PROM_URL = os.getenv("PROMETHEUS_URL")


def query_prometheus(promql: str, start: Optional[str] = None, end: Optional[str] = None):
    """If PROMETHEUS_URL is set, query Prometheus HTTP API; otherwise return a sample payload."""
    if PROM_URL:
        params = {"query": promql}
        url = PROM_URL.rstrip("/") + "/api/v1/query"
        try:
            r = requests.get(url, params=params, timeout=5)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"error": str(e)}
    else:
        # Sample / fallback
        return {
            "data": {
                "resultType": "vector",
                "result": [
                    {"metric": {"instance": "gw-a"}, "value": [1620000000, "0.995"]},
                    {"metric": {"instance": "gw-b"}, "value": [1620000000, "0.96"]},
                ],
            }
        }
