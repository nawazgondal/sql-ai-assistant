import requests
import time
from typing import Optional

# Simple cache to avoid redundant API calls
_query_cache = {}
CACHE_TTL = 3600  # 1 hour
RETRY_ATTEMPTS = 3
TIMEOUT_SECONDS = 30

def text_to_sql(question: str) -> str:
    """Convert natural language to SQL with caching and retry logic"""
    # Check cache first
    if question in _query_cache:
        cached_result, timestamp = _query_cache[question]
        if time.time() - timestamp < CACHE_TTL:
            print("[Cache Hit] Using cached SQL query")
            return cached_result

    prompt = f"""You are an expert SQL database designer.

Database schema:
- customers(id INTEGER PRIMARY KEY, name TEXT)
- orders(id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL, date TEXT)

Convert the user's natural language question into a single, valid SQL SELECT query.
Return ONLY the SQL query with no explanation or markdown formatting.

Question: {question}

SQL Query:"""

    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3  # Lower temperature for more consistent SQL
                },
                timeout=TIMEOUT_SECONDS
            )
            response.raise_for_status()
            result = response.json()
            sql_query = result["response"].strip()
            
            # CRITICAL: Query Safety - Only allow SELECT queries
            if not sql_query.lower().startswith("select"):
                print(f"[SECURITY] Blocked non-SELECT query: {sql_query[:50]}...")
                return "Only SELECT queries are allowed for security reasons."
            
            # Cache the result
            _query_cache[question] = (sql_query, time.time())
            
            return sql_query
        
        except requests.exceptions.RequestException as e:
            if attempt < RETRY_ATTEMPTS - 1:
                print(f"[Retry {attempt + 1}/{RETRY_ATTEMPTS}] API error: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"Failed to generate SQL after {RETRY_ATTEMPTS} attempts")
                raise