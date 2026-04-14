# 🚀 SQL AI Assistant

**Convert natural language to SQL queries and execute them instantly**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 What This Does

**Before:** Manual SQL writing for business questions
```sql
-- Complex query for "top customers by spending"
SELECT c.name, SUM(o.amount) as total_spending
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id
ORDER BY total_spending DESC
LIMIT 5;
```

**After:** Just ask in plain English
```
"Show me top 5 customers by total spending"
```
→ **Instant SQL + Results**

---

## 🔥 Demo Output

### API Request
```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "top 5 customers by total spending"}'
```

### API Response
```json
{
  "question": "top 5 customers by total spending",
  "sql_query": "SELECT customers.name, SUM(orders.amount) as total_spending FROM customers JOIN orders ON customers.id = orders.customer_id GROUP BY customers.id ORDER BY total_spending DESC LIMIT 5;",
  "results": [
    {"name": "Ali", "total_spending": 300.0},
    {"name": "Sara", "total_spending": 300.0},
    {"name": "Ahmed", "total_spending": 150.0}
  ],
  "row_count": 3,
  "execution_time": 1.23,
  "timestamp": "2026-04-14T23:05:41"
}
```

---

## 💼 Business Use Cases

### 📊 **Business Intelligence**
- "What's our monthly revenue trend?"
- "Which products sell best on weekends?"
- "Show customer lifetime value by region"

### 📈 **Data Analysis**
- "Find customers who haven't ordered in 30 days"
- "Average order value by customer segment"
- "Top performing sales reps this quarter"

### 🤖 **Automation**
- "Generate weekly sales summary report"
- "Alert when inventory drops below threshold"
- "Calculate customer churn risk scores"

---

## 🚀 Quick Start (3 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Ollama (if not running)
```bash
ollama pull mistral
ollama serve
```

### 3. Run API Server
```bash
python api.py
```

### 4. Test API
```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "how many customers do we have?"}'
```

---

## 📖 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/ask` | Ask natural language question |
| `GET` | `/schema` | Get database schema |
| `GET` | `/stats` | Get database statistics |
| `DELETE` | `/cache` | Clear query cache |

### Interactive Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔒 Security Features

✅ **Query Validation** - Only SELECT queries allowed  
✅ **Input Sanitization** - SQL injection prevention  
✅ **Error Isolation** - Safe exception handling  
✅ **Rate Limiting Ready** - Built for production scaling  

---

## 📊 Performance

| Metric | Value | Improvement |
|--------|-------|-------------|
| Query Generation | < 2 seconds | Cached results instant |
| Database Query | < 0.1 seconds | Indexed tables |
| API Response | < 3 seconds | Connection pooling |
| Memory Usage | < 50MB | Efficient caching |

---

## 🛠️ Development

### Run Tests
```bash
pip install -r requirements-dev.txt
pytest test_assistant.py -v
```

### Manual Testing
```bash
python test_assistant.py manual
```

---

## 💰 Freelancing Value

### Current Stage: **$50-150 gigs**
- ✅ Working API
- ✅ Database integration
- ✅ AI-powered queries
- ✅ Professional documentation

### Next Stage: **$150-300+ gigs**
- 🔄 Web UI (React/Vue)
- 🔄 Real database connections
- 🔄 Multi-tenant support
- 🔄 Advanced analytics

---

## 📄 License

MIT License - Free for commercial use

---

**Built with ❤️ for data-driven businesses**