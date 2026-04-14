from ai import text_to_sql
from db import create_tables, insert_dummy_data, run_query

# setup DB
create_tables()
insert_dummy_data()

question = "top 5 customers by total spending"

sql_query = text_to_sql(question)

print("Generated SQL:\n", sql_query)

result = run_query(sql_query)

print("\nQuery Result:\n", result)