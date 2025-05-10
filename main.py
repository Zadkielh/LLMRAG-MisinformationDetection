import faiss
import numpy as np

from typing import List
from query_processing import QueryAnalyzer, build_bigquery_filter_with_issues, build_bigquery_filter
from content_extraction import fetch_titles_for_gkg_rows, build_gkg_documents_from_rows, split_text_into_chunks_by_sentence
from external_apis import fetch_gkg_from_bigquery
from embedding_retrieval import embed_query, embed_texts, retrieve_top_chunks
from data_models import TextChunk
from llm_interaction import build_prompt_with_chunks, query_ollama

USE_ISSUES_BASED_THEME_LOGIC = True

def ask_question(question: str) -> str:
    analyzer = QueryAnalyzer()
    entities, themes, expanded_themes = analyzer.analyze_question(question)

    where_clause = build_bigquery_filter(entities, themes, expanded_themes)

    where_clause = ""
    if USE_ISSUES_BASED_THEME_LOGIC:
        print("--- Using ISSUES-BASED theme logic ---")
        entities, structured_themes_for_bq = analyzer.analyze_question_with_issues(question)
        print(f"--- Entities (Issues Logic): {entities}")
        print(f"--- Structured Themes for BQ (Issues Logic): {structured_themes_for_bq}")
        where_clause = build_bigquery_filter_with_issues(entities, structured_themes_for_bq)
    else:
        print("--- Using DIRECT LLM theme logic ---")
        entities, core_themes, expanded_themes_list = analyzer.analyze_question(question)
        print(f"--- Entities (Direct Logic): {entities}")
        print(f"--- Core Themes (Direct Logic): {core_themes}")
        print(f"--- Expanded Themes (Direct Logic): {expanded_themes_list}")
        where_clause = build_bigquery_filter(entities, core_themes, expanded_themes_list)


    print(entities, themes)

    gkg_rows = fetch_gkg_from_bigquery(where_clause, limit=500, days_to_look_back=90)

    print(f"--- Fetching titles for {len(gkg_rows)} GDELT records...")
    url_title_gkg_list = fetch_titles_for_gkg_rows(gkg_rows)

    if not url_title_gkg_list:
        return "No titles could be fetched for pre-selection."

    titles = [item[1] for item in url_title_gkg_list if item[1]]
    query_embedding = embed_query(question)

    if not titles:
        return "No valid titles found for semantic ranking."

    title_embeddings = embed_texts(titles)

    title_index = faiss.IndexFlatL2(title_embeddings.shape[1])
    title_index.add(title_embeddings)

    TOP_N_TITLES_TO_SCRAPE = 20
    distances, indices = title_index.search(query_embedding, min(TOP_N_TITLES_TO_SCRAPE, len(titles)))

    selected_gkg_rows_for_scraping = []
    print(f"--- Top {TOP_N_TITLES_TO_SCRAPE} (or fewer) semantically relevant titles/articles:")
    for i in indices[0]:
        if i != -1:
            selected_url, selected_title, original_row = url_title_gkg_list[i]
            print(f"    - {selected_title} ({selected_url})")
            selected_gkg_rows_for_scraping.append(original_row)

    if not selected_gkg_rows_for_scraping:
        return "No articles selected after title ranking for full scraping."

    gkg_documents = build_gkg_documents_from_rows(selected_gkg_rows_for_scraping)

    if not gkg_documents:
        return "Failed to fetch content for the selected relevant articles."

    all_chunks_with_meta: List[TextChunk] = []
    unique_chunk_texts = set()

    print(f"--- Chunking content from {len(gkg_documents)} documents...")
    for doc in gkg_documents:
        chunks = split_text_into_chunks_by_sentence(doc.raw_text)

        for chunk_text in chunks:
            if chunk_text not in unique_chunk_texts:
                unique_chunk_texts.add(chunk_text)
                all_chunks_with_meta.append(TextChunk(
                    text=chunk_text,
                    source_title=doc.title,
                    source_url=doc.url,
                    source_date=doc.date
                ))

    if not all_chunks_with_meta:
        return "No suitable unique text chunks found after processing documents."

    print(f"--- Generated {len(all_chunks_with_meta)} unique chunks for final retrieval.")

    chunk_texts = [chunk.text for chunk in all_chunks_with_meta]
    print(f"--- Embedding {len(chunk_texts)} unique chunks...")
    chunk_embeddings = embed_texts(chunk_texts)

    dimension = chunk_embeddings.shape[1]
    chunk_index = faiss.IndexFlatL2(dimension)

    if isinstance(chunk_embeddings, list):
        chunk_embeddings = np.array(chunk_embeddings).astype('float32')
    elif chunk_embeddings.dtype != 'float32':
        chunk_embeddings = chunk_embeddings.astype('float32')

    chunk_index.add(chunk_embeddings)
    print(f"--- Built FAISS index for unique chunks (Size: {chunk_index.ntotal}).")

    query_embedding = embed_query(question)

    NUM_CHUNKS_FOR_LLM = 10 
    print(f"--- Retrieving top {NUM_CHUNKS_FOR_LLM} relevant chunks...")
    retrieved_chunks = retrieve_top_chunks(chunk_index, all_chunks_with_meta, query_embedding, top_k=NUM_CHUNKS_FOR_LLM)

    print(f"--- Retrieved {len(retrieved_chunks)} chunks to use in prompt.")
    print("--- Top Retrieved Chunks ---")
    for i, chunk_data in enumerate(retrieved_chunks):
       print(f"--- Chunk {i+1} Source: {chunk_data.source_title} ({chunk_data.source_url})")
       print(f"--- Chunk {i+1} Text:\n{chunk_data.text}")
       print("-" * 25)

    prompt = build_prompt_with_chunks(question, retrieved_chunks)

    if not retrieved_chunks:
        return "No relevant text chunks found matching the query."
    
    print(f"--- Retrieved {len(retrieved_chunks)} chunks to use in prompt.")

    prompt = build_prompt_with_chunks(question, retrieved_chunks)

    print("--- Querying LLM with retrieved chunks...")
    return query_ollama(prompt)

    # --- End of Chunking Implementation ---


    # gkg_documents = build_gkg_documents_from_rows(selected_gkg_rows_for_scraping)

    # if not gkg_documents:
    #     return "No relevant documents found."

    # texts = [doc.raw_text for doc in gkg_documents]
    # embeddings = embed_texts(texts)

    # dimension = embeddings.shape[1]
    # index = faiss.IndexFlatL2(dimension)
    # index.add(embeddings)

    # retrieved_docs = retrieve_documents(index, gkg_documents, query_embedding)

    # print(retrieved_docs)

    # if not retrieved_docs:
    #     return "No documents matched after retrieval." # Or maybe should return the BQ results message?

    # prompt = build_prompt(question, retrieved_docs)
    # return query_ollama(prompt)

if __name__ == "__main__":
    question = "What is the political situation in Germany regarding energy policy?"
    answer = ask_question(question)
    print("\nGenerated Answer:\n", answer)