import requests

from typing import List
from data_models import GKGDocument, TextChunk
from config import OLLAMA_MODEL_NAME


def build_prompt(query: str, documents: list[GKGDocument]) -> str:
    context = ""
    for idx, doc in enumerate(documents, 1):
        context += (
            f"### ARTICLE {idx}\n"
            f"Title: {doc.title}\n"
            f"URL: {doc.url}\n"
            f"Date: {doc.date}\n"
            f"Themes: {', '.join(doc.themes)}\n"
            f"Content:\n{doc.raw_text}\n\n"
        )
    prompt = (
        f"You are a fact-based news assistant. Use only information from the articles below. "
        f"IMPORTANT: When answering, clearly mention the ARTICLE NAME OR NUMBER if you reference specific facts.\n\n"
        f"Articles:\n{context}\n"
        f"Question: {query}\n"
        f"Answer:"
    )
    return prompt

def build_prompt_with_chunks(question: str, retrieved_chunks: List[TextChunk]) -> str:
    context = ""
    if not retrieved_chunks:
        context = "No relevant information was found in the available documents.\n"
    else:
        context += "Based ONLY on the following snippets:\n\n"
        for idx, chunk in enumerate(retrieved_chunks, 1):
            context += (
                f"--- Snippet {idx} ---\n"
                f"Source: {chunk.source_title} ({chunk.source_url})\n"
                f"Date: {chunk.source_date}\n"
                f"Content Snippet:\n{chunk.text}\n\n"
            )

    prompt = (
        f"{context}"
        f"--- End of Snippets ---\n\n"
        f"Question: {question}\n\n"
        f"Instruction: You are a critical news analyst, answer the question above based ONLY on the information contained in the 'Content Snippet' sections provided. "
        f"Synthesize the information accurately and concisely. Do not add information beyond what is provided in the snippets. "
        f"If the snippets provide sufficient information, answer the question directly. "
        f"If the snippets do not contain enough information to answer the question fully, state that the provided context is insufficient or doesn't contain the answer.\n\n"
        f"IMPORTANT NOTE: When referring to any information, also provide the source. IT SHOULD BE NOTED LIKE SO: (Source - Chunk [insert number here]: [chunk title] [chunk url] )."
        f"CRUCIAL: End the generated answer with an evaluation, like so \"Label: [evaluation]\". The available labels are: \"true\", \"mostly-true\", \"half-true\", \"barely-true\", \"false\", \"pants-fire\"."
        f"Answer:"
    )
    return prompt

def query_ollama(prompt: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": OLLAMA_MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
    )
    response.raise_for_status()
    return response.json()['response']