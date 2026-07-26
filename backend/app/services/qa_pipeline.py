class QAPipeline:
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm

    def answer(self, question: str):
        return {
            "answer": "RAG pipeline placeholder. Connect the retrieval backend and LLM client to answer questions grounded in documents.",
            "sources": [],
        }
