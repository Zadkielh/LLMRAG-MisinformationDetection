import time
import requests
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
import nltk

from constants import HEADERS
from data_models import GKGDocument

nltk.download('punkt_tab')

def fetch_article_content(url: str) -> tuple[Optional[str], Optional[str]]:
    try:
        time.sleep(0.5)

        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.find('title')
        title = title_tag.string.strip() if title_tag and title_tag.string else "No Title Found"

        paragraphs = soup.find_all('p')
        text_content = [p.get_text().strip() for p in paragraphs if p.get_text() and len(p.get_text().strip()) > 50]

        if not text_content:
             all_text = soup.get_text(separator='\n', strip=True)
             text = "\n".join(line for line in all_text.splitlines() if len(line) > 20)
        else:
             text = "\n".join(text_content)

        return title, text.strip()

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error fetching {url}: {http_err}")
        return None, None
    except requests.exceptions.RequestException as req_err:
        print(f"Request error fetching {url}: {req_err}")
        return None, None
    except Exception as e:
        print(f"Failed to fetch/parse {url}: {e}")
        return None, None
    
def build_gkg_documents_from_rows(gkg_rows: List[Dict]) -> List[GKGDocument]:
    documents = []
    print(f"--- Attempting to fetch content for {len(gkg_rows)} articles...")
    for row_num, row in enumerate(gkg_rows, 1):
        url = row.get('DocumentIdentifier')
        if not url:
            print(f"--- Row {row_num}: Skipping row, missing DocumentIdentifier.")
            continue

        print(f"--- Row {row_num}: Fetching {url}")
        date_str = str(row.get('DATE'))
        title, text = fetch_article_content(url)

        if title is None or text is None or not text.strip():
            print(f"--- Row {row_num}: Failed to get valid content for {url}. Skipping.")
            continue

        themes_str = row.get('V2Themes', '')
        themes = themes_str.split(';') if themes_str else []
        tone = row.get('V2Tone', '')

        documents.append(GKGDocument(
            title=title,
            url=url,
            themes=themes,
            tone=tone,
            raw_text=text,
            date=date_str
        ))
        print(f"--- Row {row_num}: Successfully added document: {title[:50]}...")

    print(f"--- Successfully built {len(documents)} GKGDocuments.")
    return documents

def fetch_titles_for_gkg_rows(gkg_rows: List[Dict]) -> List[Tuple[str, Optional[str], Dict]]:
    titled_rows = []
    for row in gkg_rows:
        url = row.get('DocumentIdentifier')
        if not url:
            continue
        try:
            time.sleep(0.1)
            response = requests.get(url, headers=HEADERS, timeout=5, stream=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser", from_encoding=response.encoding)
            title_tag = soup.find('title')
            title = title_tag.string.strip() if title_tag and title_tag.string else "No Title Found"
            if title != "No Title Found" and len(title) > 5:
                 titled_rows.append((url, title, row))
            else:
                print(f"--- Could not fetch a valid title for {url}")

        except requests.exceptions.RequestException as e:
            print(f"--- Request error fetching title for {url}: {e}")
        except Exception as e:
            print(f"--- Error processing title for {url}: {e}")
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