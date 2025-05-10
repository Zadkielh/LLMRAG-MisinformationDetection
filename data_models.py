import faiss
import numpy as np
from typing import List
from dataclasses import dataclass

@dataclass
class GKGDocument:
    title: str
    url: str
    themes: List[str]
    tone: str
    raw_text: str
    date: str

@dataclass
class TextChunk:
    text: str
    source_title: str
    source_url: str
    source_date: str

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