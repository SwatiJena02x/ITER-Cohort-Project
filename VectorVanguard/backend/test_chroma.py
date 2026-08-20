from app.core.vector_store import collection


TEST_ID = "EV-CHROMA-TEST-001"


# Clean previous test
try:
    collection.delete(ids=[TEST_ID])
except Exception:
    pass


# Add test evidence
collection.add(
    ids=[TEST_ID],
    documents=[
        "A mobile phone was visible near the examination desk."
    ],
    metadatas=[
        {
            "evidence_id": TEST_ID,
            "source": "persistence_test",
        }
    ],
)

print("[1] Document inserted.")
print("[2] Collection count:", collection.count())


# Semantic search
results = collection.query(
    query_texts=["phone near student"],
    n_results=1,
)

print("[3] Search result IDs:", results["ids"])
print("[4] Search result documents:", results["documents"])
print("[5] Search result metadata:", results["metadatas"])


if TEST_ID in results["ids"][0]:
    print("\n[SUCCESS] Nomic + ChromaDB semantic search verified.")
else:
    print("\n[ERROR] Semantic search test failed.")