import requests

def text_to_sql(question):
    prompt = f"""
    You are a SQL expert.

    Convert the user question into SQL query.

    Database schema:
    customers(id, name)
    orders(id, customer_id, amount, date)

    Question: {question}

    Only return SQL query.
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )

    result = response.json()
    return result["response"]