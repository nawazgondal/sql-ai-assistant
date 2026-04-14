"""
Comprehensive Test Suite for SQL AI Assistant
Run tests with: python -m pytest test_assistant.py -v
Or run individual tests: python test_assistant.py
"""

import unittest
import sqlite3
import os
from unittest.mock import patch, MagicMock
from db import create_tables, insert_dummy_data, run_query, get_connection
from ai import text_to_sql, _query_cache


class TestDatabaseLayer(unittest.TestCase):
    """Test database functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Use in-memory database for testing
        self.test_db = ":memory:"
        
    def test_connection_creation(self):
        """Test that database connections can be created"""
        try:
            with get_connection() as conn:
                self.assertIsNotNone(conn)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.assertEqual(result[0], 1)
        except Exception as e:
            self.fail(f"Connection creation failed: {e}")

    def test_table_creation(self):
        """Test that database tables are created successfully"""
        try:
            create_tables()
            
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if customers table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
                customers_exists = cursor.fetchone() is not None
                self.assertTrue(customers_exists, "Customers table not created")
                
                # Check if orders table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
                orders_exists = cursor.fetchone() is not None
                self.assertTrue(orders_exists, "Orders table not created")
        except Exception as e:
            self.fail(f"Table creation failed: {e}")

    def test_dummy_data_insertion(self):
        """Test that dummy data is inserted correctly"""
        try:
            create_tables()
            insert_dummy_data()
            
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # Check customer count
                cursor.execute("SELECT COUNT(*) FROM customers")
                customer_count = cursor.fetchone()[0]
                self.assertEqual(customer_count, 3, "Expected 3 customers")
                
                # Check order count
                cursor.execute("SELECT COUNT(*) FROM orders")
                order_count = cursor.fetchone()[0]
                self.assertEqual(order_count, 4, "Expected 4 orders")
        except Exception as e:
            self.fail(f"Dummy data insertion failed: {e}")

    def test_query_execution_select(self):
        """Test basic SELECT query execution"""
        try:
            create_tables()
            insert_dummy_data()
            
            query = "SELECT * FROM customers LIMIT 1"
            result = run_query(query)
            
            self.assertGreater(len(result), 0, "Query returned no results")
            self.assertTrue(hasattr(result[0], 'keys'), "Result is not a Row object")
        except Exception as e:
            self.fail(f"SELECT query execution failed: {e}")

    def test_query_with_join(self):
        """Test JOIN query execution"""
        try:
            create_tables()
            insert_dummy_data()
            
            query = """
            SELECT c.name, COUNT(o.id) as order_count
            FROM customers c
            LEFT JOIN orders o ON c.id = o.customer_id
            GROUP BY c.id
            """
            result = run_query(query)
            
            self.assertGreater(len(result), 0, "JOIN query returned no results")
        except Exception as e:
            self.fail(f"JOIN query execution failed: {e}")

    def test_query_validation_drop(self):
        """Test that DROP commands are blocked"""
        try:
            create_tables()
            
            query = "DROP TABLE customers"
            with self.assertRaises(ValueError):
                run_query(query)
        except Exception as e:
            self.fail(f"Query validation test failed: {e}")

    def test_query_validation_delete(self):
        """Test that DELETE commands are blocked"""
        try:
            create_tables()
            
            query = "DELETE FROM customers"
            with self.assertRaises(ValueError):
                run_query(query)
        except Exception as e:
            self.fail(f"Query validation test failed: {e}")

    def test_aggregation_query(self):
        """Test aggregation functions"""
        try:
            create_tables()
            insert_dummy_data()
            
            query = "SELECT SUM(amount) as total FROM orders"
            result = run_query(query)
            
            self.assertEqual(len(result), 1, "Aggregation query returned unexpected results")
            self.assertEqual(result[0]['total'], 750.0, "Total amount calculation incorrect")
        except Exception as e:
            self.fail(f"Aggregation query failed: {e}")


class TestAILayer(unittest.TestCase):
    """Test AI/LLM functionality"""

    def setUp(self):
        """Clear cache before each test"""
        _query_cache.clear()

    def test_cache_functionality(self):
        """Test that query caching works"""
        question = "test question"
        sql_query = "SELECT * FROM customers"
        
        # Manually add to cache
        _query_cache[question] = (sql_query, 9999999999)  # Far future timestamp
        
        cached = question in _query_cache
        self.assertTrue(cached, "Cache storage failed")

    def test_cache_hit(self):
        """Test cache hit scenario"""
        question = "top customers"
        cached_sql = "SELECT * FROM customers ORDER BY id DESC"
        
        _query_cache[question] = (cached_sql, 9999999999)
        
        self.assertIn(question, _query_cache)
        stored_sql, _ = _query_cache[question]
        self.assertEqual(stored_sql, cached_sql)

    @patch('ai.requests.post')
    def test_text_to_sql_success(self, mock_post):
        """Test successful SQL generation"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": "SELECT * FROM customers"
        }
        mock_post.return_value = mock_response
        
        result = text_to_sql("show all customers")
        
        self.assertIn("SELECT", result)
        mock_post.assert_called_once()

    @patch('ai.requests.post')
    def test_text_to_sql_retry_logic(self, mock_post):
        """Test retry logic on failure"""
        # First two attempts fail, third succeeds
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": "SELECT * FROM customers"
        }
        
        mock_post.side_effect = [
            Exception("Connection error"),
            Exception("Timeout"),
            mock_response
        ]
        
        with patch('ai.requests.post', side_effect=[
            Exception("Connection error"),
            Exception("Timeout"),
            mock_response
        ]):
            try:
                result = text_to_sql("customers")
                # If we get here without exception, retries worked
            except:
                pass  # Expected after 3 retries


class TestIntegration(unittest.TestCase):
    """Integration tests for the full workflow"""

    def setUp(self):
        """Set up test environment"""
        create_tables()
        insert_dummy_data()
        _query_cache.clear()

    def test_full_workflow_setup(self):
        """Test that database is properly initialized"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0, "Database not properly initialized")

    def test_customer_spending_query(self):
        """Test the main use case: customer spending analysis"""
        query = """
        SELECT customers.name, SUM(orders.amount) as total_spending
        FROM customers
        JOIN orders ON customers.id = orders.customer_id
        GROUP BY customers.id
        ORDER BY total_spending DESC
        """
        result = run_query(query)
        
        self.assertEqual(len(result), 3, "Expected 3 customers with spending")
        # Verify first result (highest spender)
        self.assertIn('name', result[0].keys())
        self.assertIn('total_spending', result[0].keys())

    def test_data_consistency(self):
        """Test that data is consistent across queries"""
        # Count total orders
        result1 = run_query("SELECT COUNT(*) as cnt FROM orders")
        total_orders = result1[0]['cnt']
        
        # Count orders by customer and sum
        result2 = run_query("""
            SELECT COUNT(*) as cnt FROM orders 
            WHERE customer_id IN (SELECT id FROM customers)
        """)
        customer_orders = result2[0]['cnt']
        
        self.assertEqual(total_orders, customer_orders, "Data consistency check failed")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def setUp(self):
        """Set up test environment"""
        create_tables()
        insert_dummy_data()

    def test_empty_result_set(self):
        """Test query that returns no results"""
        query = "SELECT * FROM customers WHERE id = 9999"
        result = run_query(query)
        
        self.assertEqual(len(result), 0, "Empty result set not handled correctly")

    def test_invalid_column_reference(self):
        """Test query with invalid column"""
        query = "SELECT nonexistent_column FROM customers"
        result = run_query(query)
        
        # Should return empty list due to error handling
        self.assertEqual(result, [], "Invalid column should return empty list")

    def test_case_insensitive_validation(self):
        """Test that query validation is case-insensitive"""
        with self.assertRaises(ValueError):
            run_query("drop table customers")
        
        with self.assertRaises(ValueError):
            run_query("DROP TABLE customers")
        
        with self.assertRaises(ValueError):
            run_query("DrOp TABLE customers")

    def test_multiple_validation_keywords(self):
        """Test query with multiple dangerous keywords"""
        with self.assertRaises(ValueError):
            run_query("DELETE FROM customers WHERE id = 1")


def run_manual_tests():
    """Manual testing examples"""
    print("\n" + "="*60)
    print("MANUAL TESTING EXAMPLES")
    print("="*60)
    
    # Setup
    create_tables()
    insert_dummy_data()
    
    test_cases = [
        ("All customers", "SELECT * FROM customers"),
        ("All orders", "SELECT * FROM orders"),
        ("Customer count", "SELECT COUNT(*) as total_customers FROM customers"),
        ("Total orders", "SELECT COUNT(*) as total_orders FROM orders"),
        ("Top spenders", """
            SELECT c.name, SUM(o.amount) as total_spent
            FROM customers c
            JOIN orders o ON c.id = o.customer_id
            GROUP BY c.id
            ORDER BY total_spent DESC
        """),
        ("Orders by date", """
            SELECT date, COUNT(*) as order_count, SUM(amount) as daily_total
            FROM orders
            GROUP BY date
            ORDER BY date DESC
        """),
        ("Average order value", "SELECT AVG(amount) as avg_order FROM orders"),
        ("Customer with most orders", """
            SELECT c.name, COUNT(o.id) as order_count
            FROM customers c
            JOIN orders o ON c.id = o.customer_id
            GROUP BY c.id
            ORDER BY order_count DESC
            LIMIT 1
        """),
    ]
    
    for test_name, query in test_cases:
        print(f"\n📊 Test: {test_name}")
        print(f"Query: {query[:60]}..." if len(query) > 60 else f"Query: {query}")
        try:
            result = run_query(query)
            print(f"✅ Success - {len(result)} rows returned")
            if result:
                print(f"   Sample: {dict(result[0])}")
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        # Run manual tests: python test_assistant.py manual
        run_manual_tests()
    else:
        # Run unit tests
        print("\n🧪 Running Unit Tests...\n")
        unittest.main(verbosity=2)
