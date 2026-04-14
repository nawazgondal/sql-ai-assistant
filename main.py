import logging
from ai import text_to_sql
from db import create_tables, insert_dummy_data, run_query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def sanitize_query(query: str) -> str:
    """Clean and validate SQL query"""
    return query.strip()

def main():
    """Main application entry point"""
    try:
        logger.info("Initializing SQL AI Assistant...")
        
        # Setup DB
        create_tables()
        insert_dummy_data()
        logger.info("Database initialized successfully")
        
        # User question
        question = "top 5 customers by total spending"
        logger.info(f"Processing question: {question}")
        
        # Generate SQL
        sql_query = text_to_sql(question)
        sql_query = sanitize_query(sql_query)
        
        # Remove markdown formatting if present
        if sql_query.startswith("```"):
            sql_query = sql_query.split("```")[1]
            if sql_query.startswith("sql"):
                sql_query = sql_query[3:]
        
        logger.info(f"Generated SQL:\n{sql_query}")
        print("\n" + "="*50)
        print(f"Generated SQL:\n{sql_query}")
        print("="*50)
        
        # Execute query
        result = run_query(sql_query)
        
        logger.info(f"Query executed successfully. Rows returned: {len(result)}")
        print(f"\nQuery Result ({len(result)} rows):")
        for row in result:
            # Convert sqlite3.Row to dict for better display
            print(dict(row))
        print("="*50)
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)

if __name__ == "__main__":
    main()