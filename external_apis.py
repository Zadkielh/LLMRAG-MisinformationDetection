import requests
from google.cloud import bigquery
import datetime

def fetch_gdelt_themes(url: str = "http://data.gdeltproject.org/api/v2/guides/LOOKUP-GKGTHEMES.TXT") -> set:
    response = requests.get(url)
    response.raise_for_status()

    themes = set()
    for line in response.text.strip().splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        theme = parts[0].strip().upper()

        if theme and int(parts[1].strip().upper()) > 10000:
            themes.add(theme)

    return themes


def fetch_gkg_from_bigquery(where_clause: str, limit=100, days_to_look_back: int = 7) -> list[dict]:
    client = bigquery.Client()

    partition_start_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_to_look_back)).strftime('%Y-%m-%d')

    query = f"""
    SELECT
      DocumentIdentifier,
      V2Themes,
      V2Tone,
      DATE,
      V2Persons,
      V2Locations,
      V2Organizations,
      SourceCommonName
    FROM
      `gdelt-bq.gdeltv2.gkg_partitioned`
    WHERE
      _PARTITIONTIME >= TIMESTAMP("{partition_start_date}")
      AND ({where_clause})
    LIMIT {limit}
    """

    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    try:
        dry_run_job = client.query(query, job_config=job_config)
        estimated_bytes = dry_run_job.total_bytes_processed
        print(f"--- Estimated bytes to be processed: {estimated_bytes / (1024**3):.4f} GB")
        if estimated_bytes / (1024**3) > 100:
            print("--- Query cost estimate exceeds budget. Aborting.")
            return []
    except Exception as e:
        print(f"--- Error during query cost estimation: {e}")

    print(f"--- Running BigQuery Query:\n{query}")
    try:
        query_job = client.query(query)
        results = query_job.result()
        print(f"--- Query finished. Rows returned: {results.total_rows}")
        return [dict(row) for row in results]
    except Exception as e:
        print(f"--- BigQuery query failed: {e}")
        return []