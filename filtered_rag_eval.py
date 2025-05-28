import faiss
import numpy as np
import asyncio
import pandas as pd
import time

from typing import List, Any, Dict
from query_processing import QueryAnalyzer, build_bigquery_filter_with_issues_filtered
from content_extraction import fetch_titles_for_gkg_rows, build_gkg_documents_from_rows, split_text_into_chunks_by_sentence
from external_apis import fetch_gkg_from_bigquery
from embedding_retrieval import embed_query, embed_texts, retrieve_top_chunks
from data_models import TextChunk
from llm_interaction import build_prompt_with_chunks, query_ollama
from dataset_utils import adapt_liar_statement, load_liar_dataset
from sklearn.metrics import classification_report
from constants import LOW_CREDIBILITY_SOURCES

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

    filtered_sources = LOW_CREDIBILITY_SOURCES
    
    where_clause = build_bigquery_filter_with_issues_filtered(entities, structured_themes_for_bq, filtered_sources)

    print(where_clause)

    exit()

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
        return False

    print(f"--- Fetching titles for {len(gkg_rows)} GDELT records...")
    url_title_gkg_list = await fetch_titles_for_gkg_rows(gkg_rows)

    if not url_title_gkg_list:
        print("No titles could be fetched for pre-selection.")
        return False

    titles = [item[1] for item in url_title_gkg_list if item[1]]
    query_embedding = embed_query(question)

    if not titles:
        print("No valid titles found for semantic ranking.")
        return False

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
        print("No articles selected after title ranking for full scraping.")
        return False

    gkg_documents = await build_gkg_documents_from_rows(selected_gkg_rows_for_scraping)

    if not gkg_documents:
        print("Failed to fetch content for the selected relevant articles.")
        return False

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
        print("No suitable unique text chunks found after processing documents.")
        return False

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

    print(f"--- Retrieved {len(retrieved_chunks)} chunks to use in prompt.")
    print("--- Top Retrieved Chunks ---")
    for i, chunk_data in enumerate(retrieved_chunks):
       print(f"--- Chunk {i+1} Source: {chunk_data.source_title} ({chunk_data.source_url})")
       print(f"--- Chunk {i+1} Text:\n{chunk_data.text}")
       print("-" * 25)

    if not retrieved_chunks:
        print("No relevant text chunks found matching the query.")
        return False
    
    print(f"--- Retrieved {len(retrieved_chunks)} chunks to use in prompt.")

    prompt = build_prompt_with_chunks(question, retrieved_chunks)

    print("--- Querying LLM with retrieved chunks...")

    generated_answer = query_ollama(prompt)
    print("\nGenerated Answer:\n", generated_answer)
    
    predicted_label = "N/A_PARSE_ERROR"
    justification = generated_answer
    try:
        if "Label:" in generated_answer:
            label_part = generated_answer.split("Label:")[1].strip()
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

    for index, row in liar_df.head(100).iterrows():
        start_time = time.time()
        result = process_liar(row)
        if not result:
            continue
        end_time = time.time()
        result["time_taken"] = end_time - start_time
        results_list.append(result)
        print(f"--- Processed statement ID {result['id']}, Predicted: {result['predicted_label']}, Time: {result['time_taken']:.2f}s")
        
    results_df = pd.DataFrame(results_list)
    results_df.to_csv("filtered_evalutaion_results.csv", index=False)
    print("\n--- Evaluation results saved.")

    if not results_df.empty and 'true_label' in results_df.columns and 'predicted_label' in results_df.columns:
        
        valid_results_df = results_df[results_df['predicted_label'] != "N/A_PARSE_ERROR"].copy()

        if not valid_results_df.empty:
            true_labels = valid_results_df['true_label']
            predicted_labels = valid_results_df['predicted_label']

            liar_labels = ["true", "mostly-true", "half-true", "barely-true", "false", "pants-fire"]

            report_dict = classification_report(
                true_labels, 
                predicted_labels, 
                labels=liar_labels,
                zero_division=0,
                output_dict=True
            )
            
            df = pd.DataFrame(report_dict).transpose()
            df.to_csv("filtered_evaluation_class_report.csv")

        else:
            print("No valid predictions to report metrics on.")
    else:
        print("Results DataFrame is empty or missing required columns for metrics.")

    correct_preditcitons = (results_df['true_label'] == results_df['predicted_label']).sum()
    total_predictions = len(results_df)
    if total_predictions > 0:
        accuracy = correct_preditcitons / total_predictions
        print(f"Accuracy: {accuracy:.2f} ({correct_preditcitons}/{total_predictions})")


if __name__ == "__main__":
    liar_eval()
