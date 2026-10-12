# LangGraph + RAG + CopilotKit Architecture for SMSGW-AIOps

This document describes the optimized architecture that integrates LangChain/LangGraph orchestration, a RAG operational knowledge base, and CopilotKit as the AI frontend.

High-level goals:
- Make diagnosis and remediation workflows composable and auditable using a graph/state-machine (LangGraph)
- Use Retrieval-Augmented Generation (RAG) to ground LLM outputs in historical incidents, runbooks and SOPs
- Provide an interactive operator experience with CopilotKit where humans can inspect, approve and execute actions

Components:
1. Observability Layer
   - Prometheus (metrics), Loki (logs), Jaeger (traces)
   - Kafka for streaming events

2. Tools Layer (pluggable)
   - Prometheus query tool
   - Logs retrieval tool
   - Vector DB retriever (FAISS/Qdrant/Pinecone)
   - Action executors (API calls / scripts / k8s jobs)

3. Cognitive Orchestration Layer
   - LangChain for Chains and LLM integration
   - LangGraph for explicit graph/state orchestration of multi-step flows
   - Agents: MonitorAgent, DiagnoseAgent, RemedyAgent, RiskAgent, ApprovalAgent
   - Each Agent can call Tools and consult RAG

4. Knowledge Layer (RAG)
   - Documents: runbooks, postmortems, SOPs, parameter tuning guides, incident timelines
   - Embeddings: sentence-transformers
   - Vector store: FAISS (local) or Qdrant/Pinecone (managed)
   - Retriever + LLM prompt templates

5. Frontend & Human-in-the-loop
   - CopilotKit: conversation UI + tool buttons + approval workflow
   - Dashboard (Grafana) for visual metrics

6. Execution & Audit
   - All automated actions are recorded to DB (Postgres) with audit trail
   - Approval tickets for medium/high risk actions

State machine (example)
- START -> FETCH_METRICS -> ASSESS_HEALTH
- If anomaly: -> COLLECT_EVIDENCE -> QUERY_KB -> DIAGNOSE
- DIAGNOSE -> GENERATE_REMEDIES -> ASSESS_IMPACT
- If impact_low && risk_low: -> AUTO_EXECUTE
- Else: -> CREATE_APPROVAL -> WAIT_APPROVAL -> EXECUTE
- After EXECUTE -> VERIFY -> CLOSE

Safety & policies
- Low risk auto-actions only (parameter tweaks)
- Any network/channel toggles require at least 1 approver
- Rollback plan attached to each action


