# TESTING GUIDE for SQL AI Assistant

## Quick Start Testing

### 1️⃣ **Unit Tests**
Run all unit tests:
```bash
python -m pytest test_assistant.py -v
```

Run specific test class:
```bash
python -m pytest test_assistant.py::TestDatabaseLayer -v
```

Run specific test:
```bash
python -m pytest test_assistant.py::TestDatabaseLayer::test_table_creation -v
```

### 2️⃣ **Manual Testing**
Run manual test cases with sample queries:
```bash
python test_assistant.py manual
```

Or directly in Python:
```bash
python test_assistant.py
```

---

## Testing Categories

### 📊 **Database Layer Tests** (`TestDatabaseLayer`)
Tests database functionality, connection pooling, and data integrity:

| Test | What it checks |
|------|---|
| `test_connection_creation` | Database connections work |
| `test_table_creation` | Tables are created with correct schema |
| `test_dummy_data_insertion` | Sample data is inserted correctly |
| `test_query_execution_select` | SELECT queries execute properly |
| `test_query_with_join` | JOIN operations work |
| `test_query_validation_drop` | DROP commands are blocked ✅ |
| `test_query_validation_delete` | DELETE commands are blocked ✅ |
| `test_aggregation_query` | SUM, COUNT, AVG functions work |

### 🤖 **AI Layer Tests** (`TestAILayer`)
Tests LLM integration, caching, and retry logic:

| Test | What it checks |
|------|---|
| `test_cache_functionality` | Query cache stores results |
| `test_cache_hit` | Cached queries are retrieved |
| `test_text_to_sql_success` | SQL generation works (mocked) |
| `test_text_to_sql_retry_logic` | Retry logic on API failures |

### 🔗 **Integration Tests** (`TestIntegration`)
Tests full workflow from setup to execution:

| Test | What it checks |
|------|---|
| `test_full_workflow_setup` | System initializes correctly |
| `test_customer_spending_query` | Main use case works |
| `test_data_consistency` | Data integrity across queries |

### ⚠️ **Edge Cases** (`TestEdgeCases`)
Tests error handling and edge conditions:

| Test | What it checks |
|------|---|
| `test_empty_result_set` | Empty results handled gracefully |
| `test_invalid_column_reference` | Invalid queries don't crash |
| `test_case_insensitive_validation` | Security validation case-insensitive |
| `test_multiple_validation_keywords` | Multiple dangerous keywords blocked |

---

## Running Tests

### Install Test Dependencies
```bash
pip install -r requirements-dev.txt
```

### Run All Tests
```bash
pytest test_assistant.py -v
```

### Run with Coverage Report
```bash
pytest test_assistant.py --cov=. --cov-report=html
```

### Run Tests in Verbose Mode
```bash
pytest test_assistant.py -vv
```

### Run Specific Test Type
```bash
# Only database tests
pytest test_assistant.py::TestDatabaseLayer -v

# Only integration tests
pytest test_assistant.py::TestIntegration -v

# Only edge cases
pytest test_assistant.py::TestEdgeCases -v
```

### Run with Markers (if configured)
```bash
pytest test_assistant.py -m "not slow" -v
```

---

## Manual Test Cases

### Test 1: Customer Query
```bash
python -c "
from db import create_tables, insert_dummy_data, run_query
create_tables()
insert_dummy_data()
result = run_query('SELECT * FROM customers')
print(f'Found {len(result)} customers')
for row in result:
    print(dict(row))
"
```

### Test 2: Order Analysis
```bash
python -c "
from db import create_tables, insert_dummy_data, run_query
create_tables()
insert_dummy_data()
result = run_query('''
    SELECT c.name, COUNT(o.id) as orders, SUM(o.amount) as total
    FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id
''')
for row in result:
    print(dict(row))
"
```

### Test 3: Cache Testing
```bash
python -c "
from ai import text_to_sql, _query_cache
question = 'test question'
_query_cache[question] = ('SELECT * FROM customers', 9999999999)
print(f'Cache hit: {question in _query_cache}')
"
```

### Test 4: Query Validation
```bash
python -c "
from db import create_tables, run_query
create_tables()
try:
    run_query('DROP TABLE customers')
except ValueError as e:
    print(f'✅ Validation blocked: {e}')
"
```

---

## Expected Test Output

```
🧪 Running Unit Tests...

TestDatabaseLayer::test_connection_creation PASSED
TestDatabaseLayer::test_table_creation PASSED
TestDatabaseLayer::test_dummy_data_insertion PASSED
TestDatabaseLayer::test_query_execution_select PASSED
TestDatabaseLayer::test_query_with_join PASSED
TestDatabaseLayer::test_query_validation_drop PASSED
TestDatabaseLayer::test_query_validation_delete PASSED
TestDatabaseLayer::test_aggregation_query PASSED

TestAILayer::test_cache_functionality PASSED
TestAILayer::test_cache_hit PASSED
TestAILayer::test_text_to_sql_success PASSED
TestAILayer::test_text_to_sql_retry_logic PASSED

TestIntegration::test_full_workflow_setup PASSED
TestIntegration::test_customer_spending_query PASSED
TestIntegration::test_data_consistency PASSED

TestEdgeCases::test_empty_result_set PASSED
TestEdgeCases::test_invalid_column_reference PASSED
TestEdgeCases::test_case_insensitive_validation PASSED
TestEdgeCases::test_multiple_validation_keywords PASSED

===================== 21 passed in 0.45s =====================
```

---

## CI/CD Integration

### GitHub Actions Example (`.github/workflows/tests.yml`)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - run: pip install -r requirements-dev.txt
      - run: pytest test_assistant.py -v --tb=short
```

---

## Troubleshooting Tests

### Issue: "ModuleNotFoundError: No module named 'pytest'"
**Solution**: Install development dependencies
```bash
pip install -r requirements-dev.txt
```

### Issue: "Unable to connect to Ollama" during AI tests
**Solution**: This is expected - AI tests use mocking. Database tests don't need Ollama.

### Issue: "Database is locked"
**Solution**: Delete `data.db` and retry
```bash
rm data.db
pytest test_assistant.py -v
```

### Issue: Test timeout
**Solution**: Increase timeout in pytest
```bash
pytest test_assistant.py --timeout=30 -v
```

---

## Best Practices

✅ Run tests before pushing code  
✅ Add new tests for new features  
✅ Mock external API calls (Ollama)  
✅ Test edge cases and error conditions  
✅ Maintain >80% code coverage  
✅ Run full test suite in CI/CD pipeline  

---

## Test Coverage Goals

| Component | Target |
|-----------|--------|
| db.py | 90%+ |
| ai.py | 85%+ |
| main.py | 80%+ |
| Overall | 85%+ |

Check coverage:
```bash
pytest test_assistant.py --cov=. --cov-report=term-missing
```

---

## Adding New Tests

Template for new test:
```python
def test_feature_name(self):
    """Test description"""
    try:
        # Setup
        create_tables()
        
        # Execute
        result = run_query("SELECT ...")
        
        # Assert
        self.assertEqual(len(result), expected_count)
    except Exception as e:
        self.fail(f"Test failed: {e}")
```

---

Made with ❤️ for better code quality!
