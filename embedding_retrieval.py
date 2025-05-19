import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from sentence_transformers import util
from config import EMBEDDING_MODEL_NAME
from typing import List
from data_models import TextChunk, GKGDocument
from sklearn.metrics.pairwise import cosine_similarity

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

def retrieve_chunks_with_mmr(
        query_embedding: np.ndarray,
        chunk_embeddings: np.ndarray,
        all_chunks_with_meta: List[TextChunk],
        top_n_final: int = 10,
        lambda_param: float = 0.7
) -> List[TextChunk]:
    if chunk_embeddings.shape[0] == 0:
        return []
    
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)
    
    query_similarities = cosine_similarity(query_embedding, chunk_embeddings)[0]

    candidate_embeddings = chunk_embeddings
    candidate_chunks_meta = all_chunks_with_meta
    query_similarities_candidates = query_similarities

    selected_indices_in_candidates = []
    selected_chunks_final: List[TextChunk] = []

    remaining_candidate_indices = list(range(len(candidate_chunks_meta)))

    actual_top_n = min(top_n_final, len(candidate_chunks_meta))

    while len(selected_chunks_final) < actual_top_n and remaining_candidate_indices:
        mmr_scores = []
        current_best_score = -float('inf')
        current_best_idx_in_remaining = -1

        for i, idx_in_candidates in enumerate(remaining_candidate_indices):
            sim_to_query = query_similarities_candidates[idx_in_candidates]

            max_sim_to_selected = 0.0
            if selected_indices_in_candidates:
                current_candidate_embedding = candidate_embeddings[idx_in_candidates].reshape(1, -1)
                selected_embeddings = candidate_embeddings[selected_indices_in_candidates]

                sim_to_selected_list = cosine_similarity(current_candidate_embedding, selected_embeddings)[0]
                if len(sim_to_selected_list) > 0:
                    max_sim_to_selected = np.max(sim_to_selected_list)

            score = lambda_param * sim_to_query - (1 - lambda_param) * max_sim_to_selected

            if score > current_best_score:
                current_best_score = score
                current_best_idx_in_remaining = i

        if current_best_idx_in_remaining == -1:
            break

        best_actual_candidate_idx = remaining_candidate_indices.pop(current_best_idx_in_remaining)

        selected_indices_in_candidates.append(best_actual_candidate_idx)
        selected_chunks_final.append(candidate_chunks_meta[best_actual_candidate_idx])
    
    return selected_chunks_final