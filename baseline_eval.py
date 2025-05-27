import pandas as pd
import time
import pandas as pd

from dataset_utils import load_liar_dataset
from llm_interaction import query_ollama
from sklearn.metrics import classification_report

def build_baseline_prompt(statement_text: str, context: str = None, speaker: str = None, subject: str = None) -> str:
    prompt_parts = [f"Please classify the following statement: \"{statement_text}\"."]
    if speaker:
        prompt_parts.append(f" The statement was made by {speaker}.")
    if subject:
        prompt_parts.append(f" It concerns the subject of {subject}.")
    if context:
        prompt_parts.append(f" Additional context: {context}.")
    
    prompt_parts.append(
        "\nBased on the information, your task is to determine the veracity of the statement."
        "CRUCIAL: Respond with ONLY one of the following labels: "
        "\"true\", \"mostly-true\", \"half-true\", \"barely-true\", \"false\", \"pants-fire\"."
        "\nLabel:"
    )
    return "".join(prompt_parts)

def parse_llm_label(response_text: str) -> str:
    possible_labels = ["true", "mostly-true", "half-true", "barely-true", "false", "pants-fire"]
    response_lower = response_text.strip().lower()
    for label in possible_labels:
        if label in response_lower:
            return label
    print(f"Warning: Could not parse label from LLM response: '{response_text}'")
    return "N/A_PARSE_ERROR"

def process_liar_statement_baseline(liar_data_row: pd.Series) -> dict:
    statement_text = liar_data_row['statement']
    true_label = liar_data_row['label']
    statement_id = liar_data_row['id']
    context = liar_data_row.get('context', '')
    speaker = liar_data_row.get('speaker', '')
    subject = liar_data_row.get('subject', '')

    prompt = build_baseline_prompt(statement_text, context, speaker, subject)

    generated_response = query_ollama(prompt)
    
    predicted_label = parse_llm_label(generated_response)

    return {
        "id": statement_id,
        "statement": statement_text,
        "true_label": true_label,
        "predicted_label": predicted_label,
        "justification": generated_response,
        "time_taken": 0
    }

def run_baseline_liar_eval():
    liar_df = load_liar_dataset("liar/test.tsv") #
    if liar_df.empty:
        print("LIAR dataset not loaded. Exiting.")
        return

    results_list = []
    for index, row in liar_df.head(100).iterrows():
        start_time = time.time()
        result = process_liar_statement_baseline(row)
        
        if not result:
            continue
        end_time = time.time()
        result["time_taken"] = end_time - start_time
        print("--- DEBUG: Finished one")
        results_list.append(result)
        
    results_df = pd.DataFrame(results_list)
    results_df.to_csv("liar_baseline_evaluation_results.csv", index=False)
    print("\n--- Baseline evaluation results saved to liar_baseline_evaluation_results.csv")

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
            df.to_csv("liar_baseline_evaluation_class_report.csv")

        else:
            print("No valid predictions to report metrics on.")
    else:
        print("Results DataFrame is empty or missing required columns for metrics.")


    correct_predictions = (results_df['true_label'] == results_df['predicted_label']).sum()
    total_predictions = len(results_df)
    if total_predictions > 0:
        accuracy = correct_predictions / total_predictions
        print(f"Baseline Accuracy: {accuracy:.2f} ({correct_predictions}/{total_predictions})")
        precision = correct_predictions

if __name__ == "__main__":
    run_baseline_liar_eval()