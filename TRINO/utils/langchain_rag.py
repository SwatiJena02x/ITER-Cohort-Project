from __future__ import annotations

import os
from typing import Any, Dict, List, Sequence

from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

load_dotenv()


class EvidenceRAGPipeline:
    def __init__(self, persist_directory: str = "./vector_store", model_name: str = "text-embedding-3-small"):
        self.persist_directory = persist_directory
        self.model_name = model_name
        self.embeddings = OpenAIEmbeddings(model=model_name)
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name="exam_evidence",
        )
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)

    def build_documents(self, evidence_records: Sequence[Dict[str, Any]]) -> List[Document]:
        documents: List[Document] = []
        for record in evidence_records:
            content = "\n".join(
                filter(
                    None,
                    [
                        record.get("ocr_text", ""),
                        record.get("vision_description", ""),
                        record.get("category", ""),
                        record.get("camera", ""),
                        record.get("student_id", ""),
                        record.get("session_id", ""),
                    ],
                )
            )
            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "evidence_id": record.get("evidence_id", ""),
                        "student_id": record.get("student_id", ""),
                        "session_id": record.get("session_id", ""),
                        "timestamp": record.get("timestamp", ""),
                        "camera": record.get("camera", ""),
                        "category": record.get("category", ""),
                    },
                )
            )
        return documents

    def ingest_records(self, evidence_records: Sequence[Dict[str, Any]]) -> None:
        documents = self.build_documents(evidence_records)
        chunks = self.splitter.split_documents(documents)
        self.vectorstore.add_documents(chunks)

    def query(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        results = self.vectorstore.similarity_search(question, k=top_k)
        return [
            {
                "page_content": item.page_content,
                "metadata": item.metadata,
            }
            for item in results
        ]

    def route_query(self, question: str) -> str:
        lower = question.lower()
        if any(token in lower for token in ["phone", "mobile", "device", "screen", "notes"]):
            return "semantic"
        if any(token in lower for token in ["stu", "session", "student", "camera", "category"]):
            return "sql"
        return "hybrid"

    def build_chain(self):
        llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)
        template = """You are an evidence reviewer for exam investigations.
        Use only the retrieved evidence to answer the question.

        Question: {question}
        Context: {context}

        Provide a concise answer with evidence timestamps, risk notes, and a recommendation for human review.
        """
        prompt = ChatPromptTemplate.from_template(template)
        return (
            {"context": lambda x: x["context"], "question": RunnablePassthrough()}
            | prompt
            | llm
        )
