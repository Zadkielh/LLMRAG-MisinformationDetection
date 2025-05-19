import pandas as pd
from typing import List, Dict, Any

# Liar files don't come with headers
LIAR_COLUMN_NAMES = [
    "id", "label", "statement", "subject", "speaker", "speaker_job_title",
    "state_info", "party_affiliation", "barely_true_counts", "false_counts", "half_true_counts",
    "mostly_true_counts", "pants_on_fire_counts", "context"
]

def load_liar_dataset(file_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path, sep='\t', header=None, names=LIAR_COLUMN_NAMES)
        print(f"--- Successfully loaded LIAR dataset.")
        return df
    except FileNotFoundError:
        print("--- Error: LIAR dataset file not found.")
        return pd.DataFrame()
    except Exception as e:
        print(f"--- Error loaidng LIAR dataset: {e}")
        return pd.DataFrame()
    
def adapt_liar_statement(statement_details: Dict[str, Any]) -> str: 
    statement = statement_details.get('statement', '')
    speaker = statement_details.get('speaker', '')
    subject = statement_details.get('subject', '')
    context = statement_details.get('context', '')

    query = ["Gather information and evidence regarding this claim"]
    if speaker:
        query.append(f"made by {speaker}")
    if subject:
        query.append(f"on the subject of {subject}")
    if context:
        query.append(f"with the context of {context}")
    
    query.append(f": \"{statement}\"")

    query = " ".join(query)
    print(f"Formulated Query: {query}")
    return query
