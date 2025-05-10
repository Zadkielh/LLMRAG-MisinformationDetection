import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL_NAME
from typing import List
from data_models import TextChunk, GKGDocument

embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

def embed_texts(texts: List[str]) -> np.ndarray:
    embeddings = embedding_model.encode(texts, show_progress_bar=True)
    return np.array(embeddings)

def embed_query(query: str) -> np.ndarray:
    return embedding_model.encode([query])

def save_faiss_index(index: faiss.IndexFlatL2, path: str):
    try:
        faiss.write_index(index, path)
    except Exception as e:
        print(f"Failed to save FAISS index: {e}")

def retrieve_top_chunks(index: faiss.Index, 
                       all_chunks_with_meta: List[TextChunk], 
                       query_embedding: np.ndarray, 
                       top_k: int = 5) -> List[TextChunk]:

    if index.ntotal == 0:
        return []
        
    top_k = min(top_k, index.ntotal)
    distances, indices = index.search(query_embedding, top_k)
    
    retrieved_chunks = []
    for i in indices[0]:
        if i != -1 and i < len(all_chunks_with_meta):
            retrieved_chunks.append(all_chunks_with_meta[i])
            
    return retrieved_chunks

def retrieve_documents(index, gkg_documents, query_embedding: np.ndarray, top_k: int = 5) -> List[GKGDocument]:
    top_k = min(top_k, index.ntotal)
    distances, indices = index.search(query_embedding, top_k)
    retrieved_docs = [gkg_documents[i] for i in indices[0] if i != -1]
    return retrieved_docs