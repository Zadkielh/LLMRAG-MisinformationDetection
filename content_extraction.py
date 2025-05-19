import time
import requests
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
import nltk

import asyncio
import aiohttp

from constants import HEADERS
from data_models import GKGDocument

nltk.download('punkt_tab')

async def fetch_article_content(session: aiohttp.ClientSession, url: str) -> tuple[Optional[str], Optional[str]]:
    try:

        async with  session.get(url, headers=HEADERS, timeout=10) as response:
            response.raise_for_status()
            html_text = await response.text()

            soup = BeautifulSoup(html_text, "html.parser")

            title_tag = soup.find('title')
            title = title_tag.string.strip() if title_tag and title_tag.string else "No Title Found"

            paragraphs = soup.find_all('p')
            text_content_list = [p.get_text().strip() for p in paragraphs if p.get_text() and len(p.get_text().strip()) > 50]

            if not text_content_list:
                all_text = soup.get_text(seperator='\n', strip=True)
                text_content = "\n".join(line for line in all_text.splitlines() if len(line) > 20)
            else:
                text_content = "\n".join(text_content_list)

            return title, text_content.strip()
        
    except aiohttp.ClientError as e:
        print(f"AIOHTTP ClientError fetching {url}: {e}")
        return None, None
    except asyncio.TimeoutError:
        print(f"Asyncio TimeoutError fetching: {url}")
        return None, None
    except Exception as e:
        print(f"Failed to fetch/parse (async) {url}: {e}")
        return None, None
    
async def build_gkg_documents_from_rows(gkg_rows: List[Dict]) -> List[GKGDocument]:
    documents: List[GKGDocument] = []
    print(f"--- Attempting to fetch content for {len(gkg_rows)} articles...")

    async with aiohttp.ClientSession() as session:
        tasks = []
        for row_num, row in enumerate(gkg_rows, 1):
            url = row.get('DocumentIdentifier')
            if not url:
                print(f"--- Row {row_num}: Skipping row, missing DocumentIdentifier.")
                continue

            tasks.append(fetch_article_content(session, url))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            original_row = gkg_rows[i]
            url = original_row.get('DocumentIdentifier', 'N/A')

            if isinstance(result, Exception):
                print(f"--- Row {i+1}: Failed to get valid content for {url} due to an exception: {result}")
                continue

            title, text = result

            if title is None or text is None or not text.strip():
                print(f"--- Row {i+1}: Failed to get valid content for {url} (async). Skipping.")
                continue

            themes_str = original_row.get('V2Themes', '')
            themes = themes_str.split(';') if themes_str else []
            tone = original_row.get('V2Tone', '')
            date_str = str(original_row.get('DATE'))

            documents.append(GKGDocument(
                title=title, url=url, themes=themes, tone=tone, raw_text=text, date=date_str
            ))
            print(f"-- Row {i+1}: Succesfully added document (async): {title[:50]}...")

    print(f"--- Successfully build {len(documents)} GKGDocuments (async).")
    return documents

async def fetch_title_async(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    try:
        async with session.get(url, headers=HEADERS, timeout=5) as response:
            response.raise_for_status()
            html_text = await response.text()

            soup = BeautifulSoup(html_text, "html.parser")
            title_tag = soup.find('title')
            title = title_tag.string.strip() if title_tag and title_tag.string else None
            return title
    except Exception as e:
        return None

async def fetch_titles_for_gkg_rows(gkg_rows: List[Dict]) -> List[Tuple[str, Optional[str], Dict]]:
    titled_rows: List[Tuple[str, Optional[str], Dict]] = []
    urls_and_orignal_rows = []

    for row in gkg_rows:
        url = row.get('DocumentIdentifier')
        if url:
            urls_and_orignal_rows.append((url, row))
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_title_async(session, item[0]) for item in urls_and_orignal_rows]

        titles_results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(titles_results):
            url, orignal_row = urls_and_orignal_rows[i]
            if isinstance(result, Exception) or result is None or len(result) < 5:
                if not isinstance(result, Exception):
                    print(f"--- Could not fetch valid title (async) for {url}")

            else:
                title = result
                titled_rows.append((url, title, orignal_row))

    print(f"--- Fetched titles for {len(titled_rows)} out of {len(gkg_rows)} GDELT records (async).")
    return titled_rows

def split_text_into_chunks(text: str, min_chunk_words: int = 20) -> List[str]:
    chunks = []
    raw_chunks = text.split('\n\n')
    for chunk in raw_chunks:
        cleaned_chunk = chunk.strip()
        if cleaned_chunk and len(cleaned_chunk.split()) >= min_chunk_words:
            chunks.append(cleaned_chunk)
    return chunks


def split_text_into_chunks_by_sentence(text: str, sentences_per_chunk: int = 4, min_chunk_words: int = 20) -> List[str]:
    try:
        sentences = nltk.sent_tokenize(text)
    except Exception as e:
         print(f"NLTK sentence tokenization failed: {e}")
         return split_text_into_chunks(text, min_chunk_words) 

    chunks = []
    current_chunk_sentences = []
    word_count = 0
    for sentence in sentences:
        current_chunk_sentences.append(sentence)
        word_count += len(sentence.split())

        if len(current_chunk_sentences) >= sentences_per_chunk:
            chunk_text = " ".join(current_chunk_sentences).strip()
            if word_count >= min_chunk_words:
                 chunks.append(chunk_text)
            current_chunk_sentences = []
            word_count = 0

    if current_chunk_sentences:
        chunk_text = " ".join(current_chunk_sentences).strip()
        if word_count >= min_chunk_words:
             chunks.append(chunk_text)

    return chunks