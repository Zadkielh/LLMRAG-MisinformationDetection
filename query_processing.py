import spacy
import country_converter as coco
import ollama
import Levenshtein

from typing import List, Dict, Optional, Tuple, Any
from external_apis import fetch_gdelt_themes
from constants import CURATED_THEME_LIST, ISSUES_TO_GDELT_THEMES, FIPS_MANUAL_MAP
from config import OLLAMA_MODEL_NAME

class QueryAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.gdelt_themes = CURATED_THEME_LIST
        self.expanded_gdelt_themes = fetch_gdelt_themes()
        
        self.issues_map = ISSUES_TO_GDELT_THEMES
        self.issue_keys = list(self.issues_map.keys())

        self.entity_to_column = {
            "PERSON": "V2Persons",
            "GPE": "V2Locations",
            "LOC": "V2Locations",
            "ORG": "V2Organizations",
        }

        self.cc = coco.CountryConverter()

    def _parse_compound_gpe_from_org(self, org_text: str) -> List[str]:
        text_norm = org_text.upper().replace('-', ' ').replace('&', ' AND ')
        parts = [p.strip() for p in text_norm.split() if p.strip()]

        potential_country_parts = []
        if "AND" in parts:
            idx = -1
            try:
                idx = parts.index("AND")
                part1 = " ".join(parts[:idx])
                part2 = " ".join(parts[idx+1:])
                if part1: potential_country_parts.append(part1)
                if part2: potential_country_parts.append(part2)
            except ValueError:
                pass
        
        if not potential_country_parts and len(parts) >= 2:
            if '-' in org_text:
                hyphen_parts = [p.strip().upper() for p in org_text.split('-') if p.strip()]
                if len(hyphen_parts) == 2:
                    potential_country_parts = hyphen_parts


        found_fips = []
        for part in potential_country_parts:
            fips = FIPS_MANUAL_MAP.get(part)
            if not fips and (part == "US" or part == "U.S."): fips = FIPS_MANUAL_MAP.get("UNITED STATES")
            if not fips and part == "UK": fips = FIPS_MANUAL_MAP.get("UNITED KINGDOM")

            if fips:
                found_fips.append(fips)
        
        if found_fips:
            print(f"--- Dynamically parsed ORG '{org_text}' into FIPS: {found_fips}")
            return list(set(found_fips))
        return []

    def extract_entities(self, text: str) -> Dict[str, List[Tuple[str, Any]]]:
        doc = self.nlp(text)
        entity_mapping: Dict[str, List[Tuple[str, Any]]] = {
            "V2Persons": [], "V2Locations": [], "V2Organizations": []
        }
        
        processed_spacy_entity_indices = set()

        for i, ent in enumerate(doc.ents):
            if i in processed_spacy_entity_indices:
                continue

            gdelt_column = self.entity_to_column.get(ent.label_)
            if not gdelt_column:
                continue

            processed_value_for_filter: Any = None
            entity_handled_customly = False

            if ent.label_ == "ORG":
                fips_codes_from_org = self._parse_compound_gpe_from_org(ent.text)
                if fips_codes_from_org:
                    for fips_code in fips_codes_from_org:
                        entity_mapping["V2Locations"].append((f"{ent.text}_as_GPE_{fips_code}", fips_code))
                    entity_handled_customly = True
            
            if entity_handled_customly:
                processed_spacy_entity_indices.add(i)
                continue

            if ent.label_ == "GPE":
                normalized_name = ent.text.upper()
                fips_code = FIPS_MANUAL_MAP.get(normalized_name)
                if fips_code:
                    processed_value_for_filter = fips_code
                else:
                    processed_value_for_filter = ent.text
            elif ent.label_ == "PERSON":
                name_variants = self._get_person_name_variants(ent.text)
                processed_value_for_filter = name_variants if name_variants else [ent.text.title()]
            else:
                processed_value_for_filter = ent.text
            
            entity_mapping[gdelt_column].append((ent.text, processed_value_for_filter))
            processed_spacy_entity_indices.add(i)

        if "V2Locations" in entity_mapping:
            seen_loc_tuples = set()
            unique_loc_tuples = []
            for loc_tuple_original_text, loc_tuple_value in entity_mapping["V2Locations"]:
                current_tuple_repr = (loc_tuple_original_text, loc_tuple_value)
                if current_tuple_repr not in seen_loc_tuples:
                    unique_loc_tuples.append((loc_tuple_original_text, loc_tuple_value))
                    seen_loc_tuples.add(current_tuple_repr)
            entity_mapping["V2Locations"] = unique_loc_tuples
            
        return entity_mapping
    
    def _get_person_name_variants(self, name_text: str) -> List[str]:
        name_text = name_text.replace('-', ' ').title()
        parts = [p.strip() for p in name_text.split()]

        variants = set()

        if not parts:
            return []
        
        variants.add(" ".join(parts))

        if len(parts) > 1:
            variants.add(parts[-1])
            if len(parts[0]) > 1 or (len(parts[0]) == 1 and parts[0].isalpha()):
                variants.add(parts[0])
        elif len(parts) == 1:
            pass

        return list(variants)

    def extract_themes(self, text: str) -> List[str]:
        prompt = f"""
        You are an expert system designed to map user queries to a concise and highly relevant set of GDELT news themes. Your primary goal is to aid in retrieving accurate articles related to the query's core subject.

        VALID GDELT THEMES:
        {self.gdelt_themes}

        USER QUERY: '{text}'

        Instructions:
        1. Analyze the USER QUERY to understand its main subject, specific entities, and key aspects.
        2. From the VALID GDELT THEMES, select a small set that are MOST DIRECTLY and SPECIFICALLY relevant to the query's core focus.
        3. Output ONLY a COMMA-SEPARATED list of the chosen GDELT themes.
        4. Ensure all outputted themes are verbatim from the VALID GDELT THEMES list.

        Now, process the USER QUERY above.
        """

        response = ollama.chat(model=OLLAMA_MODEL_NAME, messages=[{"role": "user", "content": prompt}])
        themes_text = response['message']['content']

        raw_themes = [theme.strip().upper() for theme in themes_text.split(',') if theme.strip()]
        valid_themes = [theme for theme in raw_themes if theme in self.gdelt_themes]
        other_themes = []

        for theme in raw_themes:
            if theme in self.gdelt_themes:
                valid_themes.append(theme)
            else:
                other_themes.append(theme)

        expanded_themes = []

        for theme in other_themes:
            for ex_theme in self.expanded_gdelt_themes:
                if Levenshtein.ratio(theme, ex_theme) > 0.6:
                    expanded_themes.append(ex_theme)

        unique_themes = list(set(valid_themes))
        expanded_themes = list(set(expanded_themes))


        print(f"--- Raw Themes from LLM: {raw_themes}")
        print(f"--- Filtered & Unique Themes: {unique_themes}")
        print(f"--- Expanded Themes: {expanded_themes}")
        
        return unique_themes, expanded_themes
    
    def _map_query_to_issue_categories(self, query: str) -> List[str]:
        issue_keys_str = ", ".join(self.issue_keys)
        prompt = f"""
        Given the user query: "{query}"
        And the following available high-level issue categories: {issue_keys_str}

        Which of these issue categories are MOST relevant to the user query?
        Consider the primary subject and any specific aspects mentioned.
        Return a comma-separated list of of the most CENTRAL and DOMINANT category keys from the provided list.
        For example, for "German energy policy", relevant categories might be "energy, partypolitics, internationalrelations".
        For "Impact of new tariffs on US steel imports", relevant categories might be "trade, domesticeconomy".
        Output only the comma-separated keys. If no categories seem relevant, output 'NO_CATEGORY_MATCH'.
        """
        response = ollama.chat(model=OLLAMA_MODEL_NAME, messages=[{"role": "user", "content": prompt}])
        matched_keys_text = response['message']['content']
        print(f"--- LLM output for issue categories: {matched_keys_text}")

        if "NO_CATEGORY_MATCH" in matched_keys_text.upper(): return []
        
        matched_keys = [key.strip().lower() for key in matched_keys_text.split(',') if key.strip().lower() in self.issue_keys]
        print(f"--- Query mapped to issue categories: {matched_keys}")
        return matched_keys

    def analyze_question_with_issues(self, question: str) -> Tuple[Dict[str, List[Tuple[str, Optional[str]]]], Dict[str, List[str]]]:
        entities = self.extract_entities(question)
        matched_issue_keys = self._map_query_to_issue_categories(question)
        
        structured_gdelt_themes = {}
        if matched_issue_keys:
            for key in matched_issue_keys:
                themes_for_key = self.issues_map.get(key)
                if themes_for_key:
                    structured_gdelt_themes[key] = themes_for_key
        
        print(f"--- Structured GDELT themes (from issues map) for BigQuery: {structured_gdelt_themes}")
        return entities, structured_gdelt_themes

    def analyze_question(self, question: str) -> Tuple[Dict[str, List[Tuple[str, Optional[str]]]], List[str]]:
        entities = self.extract_entities(question)
        themes, expanded_themes = self.extract_themes(question)
        return entities, themes, expanded_themes
    
def build_bigquery_filter_with_issues(entities: Dict[str, List[Tuple[str, Any]]],
                                      structured_themes: Dict[str, List[str]],
                                     loose: bool = False) -> str:
    category_clauses = []

    for column, values in entities.items():
        if not values: continue
        
        likes = []
        for original_text, value_for_filter in values:

            if column == "V2Locations" and isinstance(value_for_filter, str) and value_for_filter in FIPS_MANUAL_MAP.values():
                fips_code = value_for_filter
                likes.append(f"EXISTS (SELECT 1 FROM UNNEST(SPLIT({column}, ';')) AS loc_item WHERE TRIM(SPLIT(loc_item, '#')[SAFE_OFFSET(2)]) = '{fips_code}')")
            elif column == "V2Locations" and isinstance(value_for_filter, str):
                likes.append(f"{column} LIKE '%{value_for_filter.replace("'", "''")}%'")
            elif column == "V2Persons" and isinstance(value_for_filter, list):
                person_variant_likes = []
                for variant in value_for_filter:
                    safe_variant = variant.replace("'", "''")
                    person_variant_likes.append(f"{column} LIKE '%{safe_variant}%'")
                if person_variant_likes:
                    likes.append(f"({' OR '.join(person_variant_likes)})")
            elif isinstance(value_for_filter, str):
                likes.append(f"{column} LIKE '%{value_for_filter.replace("'", "''")}%'")

        if likes: 
            category_clauses.append(f"({' OR '.join(likes)})")

    entity_filter_str = " AND ".join(category_clauses) if category_clauses else "1=1"

    issue_group_clauses = []
    if structured_themes:
        for issue_key, theme_list_for_issue in structured_themes.items():
            if theme_list_for_issue:
                safe_themes_for_issue = [theme.replace("'", "''") for theme in theme_list_for_issue]
                theme_likes_for_issue = [f"V2Themes LIKE '%{th}%'" for th in safe_themes_for_issue]
                issue_group_clauses.append(f"({' OR '.join(theme_likes_for_issue)})")
    
    combined_theme_filter_str = "1=1"
    if issue_group_clauses:
        if loose:
            combined_theme_filter_str = f"({' OR '.join(issue_group_clauses)})"
            print("--- Using LOOSE theme filter logic (OR between issue groups).")
        else:
            combined_theme_filter_str = f"({' AND '.join(issue_group_clauses)})"
            print("--- Using STRICT theme filter logic (AND between issue groups).")

    if entity_filter_str != "1=1" and combined_theme_filter_str != "1=1":
        final_filter = f"({entity_filter_str}) AND ({combined_theme_filter_str})"
    elif entity_filter_str != "1=1":
        final_filter = entity_filter_str
    elif combined_theme_filter_str != "1=1":
        final_filter = combined_theme_filter_str
    else:
        final_filter = "1=1"

    if final_filter == "1=1":
        print("--- Warning: No specific entity or theme filters generated (issues-based).")
    print(f"--- Generated BigQuery Filter (issues-based, loose={loose}): {final_filter}")
    return final_filter


def build_bigquery_filter(entities: Dict[str, List[Tuple[str, Optional[str]]]], themes: List[str], expanded_themes: List[str]) -> str:
    """ Builds filter using entities (text, code) and themes """
    entity_filters = []
    theme_filters = []

    category_clauses = []
    for column, values in entities.items():
        if not values:
            continue

        likes = []
        for original_text, code in values:
            safe_text = original_text.replace("'", "''")

            if column == "V2Locations" and code:
                likes.append(f"{column} LIKE '%#{code}#%'")
            else:
                likes.append(f"{column} LIKE '%{safe_text}%'")

        if likes:
            category_clauses.append(f"({' OR '.join(likes)})")

    entity_filter_str = " AND ".join(category_clauses) if category_clauses else "1=1"

    core_theme_clause_str = ""
    if themes:
        safe_core_themes = [theme.replace("'", "''") for theme in themes]
        if len(safe_core_themes) == 1:
            core_theme_clause_str = f"(V2Themes LIKE '%{safe_core_themes[0]}%')"
        elif len(safe_core_themes) > 1:
            core_theme_likes = [f"V2Themes LIKE '%{theme}%'" for theme in safe_core_themes]
            core_theme_clause_str = f"({' AND '.join(core_theme_likes)})"

    expanded_theme_clause_str = ""
    if expanded_themes:
        safe_expanded_themes = [theme.replace("'", "''") for theme in expanded_themes]
        if len(safe_expanded_themes) == 1:
            expanded_theme_clause_str = f"(V2Themes LIKE '%{safe_expanded_themes[0]}%')"
        elif len(safe_expanded_themes) > 1:
            expanded_theme_likes = [f"V2Themes LIKE '%{theme}%'" for theme in safe_expanded_themes]
            expanded_theme_clause_str = f"({' OR '.join(expanded_theme_likes)})"

    final_theme_clauses = []
    if core_theme_clause_str:
        final_theme_clauses.append(core_theme_clause_str)
    if expanded_theme_clause_str:
        final_theme_clauses.append(expanded_theme_clause_str)
    
    combined_theme_filter_str = "1=1"
    if final_theme_clauses:
        combined_theme_filter_str = " AND ".join(final_theme_clauses)


    if entity_filter_str != "1=1" and combined_theme_filter_str != "1=1":
        final_filter = f"({entity_filter_str}) AND ({combined_theme_filter_str})"
    elif entity_filter_str != "1=1":
        final_filter = entity_filter_str
    elif combined_theme_filter_str != "1=1":
        final_filter = combined_theme_filter_str
    else:
        final_filter = "1=1"

    if final_filter == "1=1":
        print("--- Warning: No specific entity or theme filters generated by build_bigquery_filter.")

    print(f"--- Generated BigQuery Filter: {final_filter}")
    return final_filter