"""
Command-line runner for the DSA Coach Tree RAG Agent.
"""
from agent.tree_agent import graph

def main():
    print("DSA COACH TREE - LANGGRAPH RAG AGENT")
    print("-" * 70)
    print("\nType 'exit' to stop.\n")

    # Same thread_id means the agent can maintain
    # conversation state during this program execution.

    config = {"configurable": {"thread_id": "demo-user-1"}}

    while True:
        question = input("\nStudent: ").strip()
        if question.lower() in {"exit","quit"}:
            print("\nGoodbye!")
            break

        if not question:
            continue

        try:
            result = graph.invoke({"messages": [{"role": "user", "content": question}]},config=config)
            final_message = result["messages"][-1]
            print("\nDSA Coach:")
            print("-" * 70)
            print(final_message.content)
            print("-" * 70)

        except Exception as error:
            print("\nERROR:")
            print(error)

if __name__ == "__main__":
    main()

