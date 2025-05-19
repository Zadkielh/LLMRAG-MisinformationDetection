import faiss
import numpy as np
import asyncio
import pandas as pd
import time

from typing import List, Any, Dict
from query_processing import QueryAnalyzer, build_bigquery_filter_with_issues, build_bigquery_filter
from content_extraction import fetch_titles_for_gkg_rows, build_gkg_documents_from_rows, split_text_into_chunks_by_sentence
from external_apis import fetch_gkg_from_bigquery
from embedding_retrieval import embed_query, embed_texts, retrieve_top_chunks, retrieve_chunks_with_mmr
from data_models import TextChunk
from llm_interaction import build_prompt_with_chunks, query_ollama
from dataset_utils import adapt_liar_statement, load_liar_dataset

USE_ISSUES_BASED_THEME_LOGIC = True

def process_liar(liar_data_row: pd.Series) -> Dict[str, Any]:
    statement_text = liar_data_row['statement']
    label = liar_data_row['label']
    speaker = liar_data_row['speaker']
    subject = liar_data_row['subject']
    context = liar_data_row['context']

    query = adapt_liar_statement(liar_data_row.to_dict())

    return asyncio.run(ask_question(query, statement_text, label, liar_data_row['id']))


async def ask_question(question: str, statement_text: str, label: str, id) -> str:
    analyzer = QueryAnalyzer()

    where_clause = ""
    
    entities, structured_themes_for_bq = analyzer.analyze_question_with_issues(question)

    print("--- SNIP ---")
    print(structured_themes_for_bq)
    print(entities)
    print("--- SNIP ---")
    
    where_clause = build_bigquery_filter_with_issues(entities, structured_themes_for_bq)

    gkg_rows = fetch_gkg_from_bigquery(where_clause, limit=500, days_to_look_back=90)

    if len(gkg_rows) <= 0:
        entities['V2Organizations'] = None
        looser_themes = structured_themes_for_bq
        
        while len(looser_themes) > 1:
            looser_themes.popitem()
        
        where_clause = build_bigquery_filter_with_issues(entities, looser_themes, loose=True)
        gkg_rows = fetch_gkg_from_bigquery(where_clause, limit=500, days_to_look_back=90)

    if len(gkg_rows) <= 0:
        print("--- No articles found, exiting!")
        exit()

    print(f"--- Fetching titles for {len(gkg_rows)} GDELT records...")
    url_title_gkg_list = await fetch_titles_for_gkg_rows(gkg_rows)

    if not url_title_gkg_list:
        return "No titles could be fetched for pre-selection."

    titles = [item[1] for item in url_title_gkg_list if item[1]]
    query_embedding = embed_query(question)

    if not titles:
        return "No valid titles found for semantic ranking."

    title_embeddings = embed_texts(titles)

    title_index = faiss.IndexFlatL2(title_embeddings.shape[1])
    title_index.add(title_embeddings)

    TOP_N_TITLES_TO_SCRAPE = 30
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

    gkg_documents = await build_gkg_documents_from_rows(selected_gkg_rows_for_scraping)

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
    LAMBDA_MMR = 0.7

    print(f"--- Retrieving top {NUM_CHUNKS_FOR_LLM} relevant chunks...")
    retrieved_chunks = retrieve_top_chunks(chunk_index, all_chunks_with_meta, query_embedding, top_k=NUM_CHUNKS_FOR_LLM)

    # print(f"--- Retrieving top {NUM_CHUNKS_FOR_LLM} relevant and diverse chunks using MMR (lambda={LAMBDA_MMR})...")
    # retrieved_chunks = retrieve_chunks_with_mmr(
    #     query_embedding,
    #     chunk_embeddings, # Pass the numpy array of embeddings
    #     all_chunks_with_meta,
    #     top_n_final=NUM_CHUNKS_FOR_LLM,
    #     lambda_param=LAMBDA_MMR
    # )

    # if not retrieved_chunks:
    #     return "No relevant text chunks found after MMR."
    
    # print(f"--- Retrieved {len(retrieved_chunks)} chunks using MMR to use in prompt.")
    # # (Your existing chunk printing loop for debugging)
    # print("--- Top Retrieved Chunks (MMR) ---")
    # for i, chunk_data in enumerate(retrieved_chunks):
    #    print(f"--- Chunk {i+1} Source: {chunk_data.source_title} ({chunk_data.source_url})")
    #    print(f"--- Chunk {i+1} Text:\n{chunk_data.text}")
    #    print("-" * 25)


    print(f"--- Retrieved {len(retrieved_chunks)} chunks to use in prompt.")
    print("--- Top Retrieved Chunks ---")
    for i, chunk_data in enumerate(retrieved_chunks):
       print(f"--- Chunk {i+1} Source: {chunk_data.source_title} ({chunk_data.source_url})")
       print(f"--- Chunk {i+1} Text:\n{chunk_data.text}")
       print("-" * 25)

    if not retrieved_chunks:
        return "No relevant text chunks found matching the query."
    
    print(f"--- Retrieved {len(retrieved_chunks)} chunks to use in prompt.")

    prompt = build_prompt_with_chunks(question, retrieved_chunks)

    print("--- Querying LLM with retrieved chunks...")

    generated_answer = query_ollama(prompt)
    print("\nGenerated Answer:\n", generated_answer)
    
    # 5. Parse LLM response to get label and justification (this needs robust parsing)
    # Example simple parsing (you'll need to make this more robust)
    predicted_label = "N/A_PARSE_ERROR"
    justification = generated_answer # Default to full response if parsing fails
    try:
        if "Label:" in generated_answer:
            label_part = generated_answer.split("Label:")[1].strip()
            # LIAR labels: true, mostly-true, half-true, barely-true, false, pants-fire
            possible_labels = ["true", "mostly-true", "half-true", "barely-true", "false", "pants-fire"]
            for l in possible_labels:
                if label_part.lower().startswith(l):
                    predicted_label = l
                    break
        if "Justification:" in generated_answer:
             justification = generated_answer.split("Justification:")[1].split("Label:")[0].strip()

    except Exception as e:
        print(f"Error parsing LLM response: {e}")

    return {
        "id": id,
        "statement": statement_text,
        "true_label": label,
        "predicted_label": predicted_label,
        "justification": justification,
        "time_taken": 0
    }
    


def liar_eval():
    liar_df = load_liar_dataset("liar/test.tsv")
    if liar_df.empty:
        return

    results_list = []

    for index, row in liar_df.head(5).iterrows():
        start_time = time.time()
        result = process_liar(row)
        end_time = time.time()
        result["time_taken"] = end_time - start_time
        results_list.append(result)
        print(f"--- Processed statement ID {result['id']}, Predicted: {result['predicted_label']}, Time: {result['time_taken']:.2f}s")
        
    results_df = pd.DataFrame(results_list)
    results_df.to_csv("liar_evalutaion_results.csv", index=False)
    print("\n--- Evaluation results saved.")

    correct_preditcitons = (results_df['true_label'] == results_df['predicted_label']).sum()
    total_predictions = len(results_df)
    if total_predictions > 0:
        accuracy = correct_preditcitons / total_predictions
        print(f"Accuracy: {accuracy:.2f} ({correct_preditcitons}/{total_predictions})")


if __name__ == "__main__":
    # question = "What is the political situation in Germany regarding energy policy?"
    # answer = asyncio.run(ask_question(question))
    # print("\nGenerated Answer:\n", answer)

    liar_eval()

    # Feed Liar statement into LLM as a question
    # Extract subject, speaker, party affiliation and context
    # Validate against label
    # Record and display statistics like time spent per statement, accuracy, etc.