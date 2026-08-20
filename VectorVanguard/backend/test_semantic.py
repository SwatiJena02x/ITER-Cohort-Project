import sys

from app.core.vector_store import collection
from app.services.retrieval import SemanticRetriever


TEST_EVIDENCE_ID = "EV-SEMANTIC-TEST"


def run_test():
    print("[*] 1. Adding temporary semantic test document...")

    collection.add(
        ids=[TEST_EVIDENCE_ID],
        documents=[
            "A mobile phone was visible near the examination desk."
        ],
        metadatas=[
            {
                "evidence_id": TEST_EVIDENCE_ID,
                "session_id": "SEMANTIC-TEST-SESSION",
            }
        ],
    )

    try:
        print("[*] 2. Testing semantic search...")

        retriever = SemanticRetriever()

        query = "Was there a cellphone near the desk?"

        print(f"  -> Query: '{query}'")

        results = retriever.search(
            query=query,
            top_k=5,
        )

        if not results:
            print("\n[ERROR] No semantic results found.")
            return False

        print("\n[SUCCESS] Semantic Match Found!")

        for result in results:
            print(f"  -> Evidence ID: {result['evidence_id']}")
            print(f"  -> Distance: {result['score']}")
            print(f"  -> Document: {result['ocr_text']}")

        return results[0]["evidence_id"] == TEST_EVIDENCE_ID

    finally:
        print("\n[*] 3. Cleaning up semantic test data...")

        collection.delete(
            ids=[TEST_EVIDENCE_ID]
        )

        print("[*] Test data removed.")


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)