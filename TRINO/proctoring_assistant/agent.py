from __future__ import annotations

from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, START, StateGraph

from .retrieval_agent import analyze_query


class AgentState(TypedDict, total=False):
    user_query: str
    query_type: str
    filters: Dict[str, Any]
    retrieved_documents: List[Dict[str, Any]]
    reranked_documents: List[Dict[str, Any]]
    final_answer: str
    evidence_references: List[str]
    top_k: int
    use_ollama: bool
    ollama_url: str
    ollama_model: str


def build_agent_graph(service: Any):
    workflow = StateGraph(AgentState)

    def query_analysis(state: AgentState) -> AgentState:
        analysis = analyze_query(state.get("user_query", ""))
        return {
            **state,
            "query_type": analysis["query_type"],
            "filters": analysis["filters"],
        }

    def route_query_node(state: AgentState) -> AgentState:
        return state

    def semantic_retrieval(state: AgentState) -> AgentState:
        documents = service.semantic_retrieval(state["user_query"], state.get("top_k", 10))
        return {**state, "retrieved_documents": documents}

    def sql_retrieval(state: AgentState) -> AgentState:
        documents = service.sql_retrieval(state.get("filters", {}), state.get("top_k", 10))
        return {**state, "retrieved_documents": documents}

    def hybrid_retrieval(state: AgentState) -> AgentState:
        documents = service.hybrid_retrieval(
            state["user_query"], state.get("filters", {}), state.get("top_k", 10)
        )
        return {**state, "retrieved_documents": documents}

    def top_k_limit(state: AgentState) -> AgentState:
        return {**state, "retrieved_documents": state.get("retrieved_documents", [])[: state.get("top_k", 10)]}

    def reranking(state: AgentState) -> AgentState:
        documents = service.rerank(
            state.get("user_query", ""),
            state.get("retrieved_documents", []),
            state.get("top_k", 10),
        )
        return {**state, "reranked_documents": documents}

    def rag_generation(state: AgentState) -> AgentState:
        documents = state.get("reranked_documents", [])
        answer = service.generate_rag_answer(
            state.get("user_query", ""),
            documents,
            ollama_url=state.get("ollama_url", "http://localhost:11434"),
            ollama_model=state.get("ollama_model", "llama3.1"),
            use_ollama=state.get("use_ollama", False),
        )
        references = [item["metadata"]["evidence_id"] for item in documents if item.get("metadata", {}).get("evidence_id")]
        return {**state, "final_answer": answer, "evidence_references": references}

    workflow.add_node("query_analysis", query_analysis)
    workflow.add_node("route_query", route_query_node)
    workflow.add_node("semantic_retrieval", semantic_retrieval)
    workflow.add_node("sql_retrieval", sql_retrieval)
    workflow.add_node("hybrid_retrieval", hybrid_retrieval)
    workflow.add_node("top_k_limit", top_k_limit)
    workflow.add_node("reranking", reranking)
    workflow.add_node("rag_generation", rag_generation)
    workflow.add_edge(START, "query_analysis")
    workflow.add_edge("query_analysis", "route_query")
    workflow.add_conditional_edges(
        "route_query",
        lambda state: state["query_type"],
        {
            "SEMANTIC": "semantic_retrieval",
            "SQL": "sql_retrieval",
            "HYBRID": "hybrid_retrieval",
        },
    )
    for retrieval_node in ("semantic_retrieval", "sql_retrieval", "hybrid_retrieval"):
        workflow.add_edge(retrieval_node, "top_k_limit")
    workflow.add_edge("top_k_limit", "reranking")
    workflow.add_edge("reranking", "rag_generation")
    workflow.add_edge("rag_generation", END)
    return workflow.compile()
