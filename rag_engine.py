import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, TOP_K_RESULTS

class RAGEngine:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.index = None
        self.products_data = []

    def build_index(self, products):
        if not products:
            print("No products to index.")
            return
            
        print("Building vector index...")
        self.products_data = products
        texts = []
        for p in products:
            rich_text = f"{p.get('Full Name', '')} {p.get('Brand', '')} {p.get('CPU', '')} {p.get('RAM', '')} {p.get('GPU', '')}"
            texts.append(rich_text)
            
        embeddings = self.model.encode(texts)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        print(f"Index built successfully with {len(products)} products")

    def search(self, query):
        if self.index is None:
            return []
            
        query_embedding = self.model.encode([query])
        distances, ids = self.index.search(np.array(query_embedding).astype('float32'), TOP_K_RESULTS)
        
        results = []
        for i in ids[0]:
            if i != -1 and i < len(self.products_data):
                results.append(self.products_data[i])
        return results