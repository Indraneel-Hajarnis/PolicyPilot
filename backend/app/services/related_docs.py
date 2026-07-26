class RelatedDocsService:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def suggest(self, document_id: int, top_k: int = 5):
        return []
