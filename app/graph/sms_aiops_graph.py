import os
from typing import Dict, Any

from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from app.rag.kb_loader import get_retriever


class LangGraphOrchestrator:
    def __init__(self, llm=None):
        # llm: a LangChain LLM; if None, try OpenAI from environment
        self.llm = llm or (OpenAI() if os.getenv("OPENAI_API_KEY") else None)
        self.retriever = get_retriever()
        self.prompt = PromptTemplate(
            input_variables=["context", "metrics"],
            template=(
                "You are an SMS Gateway AIOps assistant. Use the context from runbooks and historical incidents:\n"
                "{context}\n\nMetrics snapshot: {metrics}\n\nProvide a concise diagnosis of root cause and 3 possible actions with risk levels."
            ),
        )

    def diagnose_with_rag(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        # Build RetrievalQA if llm available
        if self.llm:
            qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=self.retriever)
            query = f"Metrics snapshot: {metrics} - give diagnosis and recommended actions"
            answer = qa.run(query)
            return {"llm_answer": answer}
        else:
            # fallback: use retriever + simple template
            docs = self.retriever.get_relevant_documents(str(metrics))
            context = "\n---\n".join([d.page_content[:1000] for d in docs])
            prompt = self.prompt.format(context=context, metrics=metrics)
            # No LLM: return prompt and top docs for human operator
            return {
                "prompt_for_llm": prompt,
                "evidence_docs": [d.metadata.get("source") for d in docs],
            }

    def run_diagnosis_flow(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        # High-level orchestration
        # 1. quick health scoring (lightweight)
        # 2. if anomaly -> do RAG + LLM diagnosis
        from app.core.monitoring import MonitoringEngine

        aggr = MonitoringEngine.aggregate_health(list(metrics.values()))
        result = {"aggregate": aggr}

        if aggr.get("unhealthy_gateways"):
            rag_result = self.diagnose_with_rag(metrics)
            result["rag"] = rag_result
        else:
            result["note"] = "No significant anomalies detected"

        return result
