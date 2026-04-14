"""
FastAPI SQL AI Assistant
REST API for natural language to SQL conversion and execution
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import time
from datetime import datetime

from ai import text_to_sql
from db import create_tables, insert_dummy_data, run_query
from config import LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SQL AI Assistant API",
    description="Convert natural language questions to SQL and execute them",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QueryRequest(BaseModel):
    question: str
    max_rows: Optional[int] = 100

class QueryResponse(BaseModel):
    question: str
    sql_query: str
    results: List[Dict[str, Any]]
    row_count: int
    execution_time: float
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

# Global variables for initialization
_db_initialized = False

def initialize_database():
    """Initialize database on first request"""
    global _db_initialized
    if not _db_initialized:
        logger.info("Initializing database...")
        create_tables()
        insert_dummy_data()
        _db_initialized = True
        logger.info("Database initialized successfully")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    initialize_database()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest, background_tasks: BackgroundTasks):
    """Convert natural language question to SQL and execute it"""
    start_time = time.time()

    try:
        logger.info(f"Processing question: {request.question}")

        # Generate SQL from natural language
        sql_query = text_to_sql(request.question)

        # Check if query generation failed
        if "Only SELECT queries are allowed" in sql_query:
            raise HTTPException(
                status_code=400,
                detail="Query generation failed: Only SELECT queries are allowed"
            )

        logger.info(f"Generated SQL: {sql_query}")

        # Execute query
        results = run_query(sql_query)

        # Convert sqlite3.Row objects to dictionaries
        formatted_results = [dict(row) for row in results]

        # Limit results if specified
        if request.max_rows and len(formatted_results) > request.max_rows:
            formatted_results = formatted_results[:request.max_rows]

        execution_time = time.time() - start_time

        logger.info(f"Query executed successfully. Rows: {len(formatted_results)}, Time: {execution_time:.2f}s")

        return QueryResponse(
            question=request.question,
            sql_query=sql_query,
            results=formatted_results,
            row_count=len(formatted_results),
            execution_time=round(execution_time, 2),
            timestamp=datetime.now().isoformat()
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/schema")
async def get_schema():
    """Get database schema information"""
    try:
        # Get table information
        tables_query = """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """
        tables = run_query(tables_query)

        schema_info = {}
        for table in tables:
            table_name = table['name']

            # Get column information
            columns_query = f"PRAGMA table_info({table_name})"
            columns = run_query(columns_query)

            # Get sample data
            sample_query = f"SELECT * FROM {table_name} LIMIT 3"
            sample_data = run_query(sample_query)

            schema_info[table_name] = {
                "columns": [dict(col) for col in columns],
                "sample_data": [dict(row) for row in sample_data],
                "row_count": len(sample_data)
            }

        return {
            "database": "SQLite",
            "tables": schema_info,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Schema retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve schema")

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        stats = {}

        # Table counts
        tables = run_query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        for table in tables:
            table_name = table['name']
            count = run_query(f"SELECT COUNT(*) as count FROM {table_name}")[0]['count']
            stats[f"{table_name}_count"] = count

        # Cache stats
        from ai import _query_cache
        stats["cache_entries"] = len(_query_cache)

        return {
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Stats retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve stats")

@app.delete("/cache")
async def clear_cache():
    """Clear the query cache"""
    try:
        from ai import _query_cache
        cache_size = len(_query_cache)
        _query_cache.clear()

        logger.info(f"Cache cleared: {cache_size} entries removed")

        return {
            "message": f"Cache cleared successfully",
            "entries_removed": cache_size,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting SQL AI Assistant API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔄 Alternative Docs: http://localhost:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000)