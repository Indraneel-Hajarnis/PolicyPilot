class Retriever:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def retrieve(self, query_embedding, top_k=5):
        return self.vector_store.search(query_embedding, top_k=top_k)
