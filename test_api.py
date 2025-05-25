"""
Simple test script for the Book Management API
Run this after starting the API server to test basic functionality
"""

import requests
import base64
import json
from datetime import date

# API base URL
BASE_URL = "http://localhost:8000"

# Authentication credentials
USERNAME = "admin"
PASSWORD = "password123"

def get_auth_headers():
    """Get basic auth headers"""
    credentials = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {credentials}"}

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("✅ Health check passed")

def test_add_book():
    """Test adding a new book"""
    print("📚 Testing add book...")
    book_data = {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "published_date": "1925-04-10",
        "number_of_pages": 180
    }
    
    response = requests.post(
        f"{BASE_URL}/api/books",
        json=book_data,
        headers=get_auth_headers()
    )
    
    assert response.status_code == 201
    book = response.json()
    assert book["title"] == book_data["title"]
    assert "id" in book
    print(f"✅ Book added with ID: {book['id']}")
    return book["id"]

def test_get_all_books():
    """Test getting all books"""
    print("📖 Testing get all books...")
    response = requests.get(f"{BASE_URL}/api/books")
    assert response.status_code == 200
    
    data = response.json()
    assert "books" in data
    assert "total" in data
    assert "page" in data
    print(f"✅ Retrieved {data['total']} books")

def test_get_book_by_id(book_id):
    """Test getting a specific book"""
    print(f"🔍 Testing get book by ID: {book_id}")
    response = requests.get(f"{BASE_URL}/api/books/{book_id}")
    assert response.status_code == 200
    
    book = response.json()
    assert book["id"] == book_id
    print(f"✅ Retrieved book: {book['title']}")

def test_update_book(book_id):
    """Test updating a book"""
    print(f"✏️ Testing update book ID: {book_id}")
    update_data = {
        "title": "The Great Gatsby - Updated Edition",
        "number_of_pages": 200
    }
    
    response = requests.put(
        f"{BASE_URL}/api/books/{book_id}",
        json=update_data,
        headers=get_auth_headers()
    )
    
    assert response.status_code == 200
    book = response.json()
    assert book["title"] == update_data["title"]
    assert book["number_of_pages"] == update_data["number_of_pages"]
    print("✅ Book updated successfully")

def test_delete_book(book_id):
    """Test deleting a book"""
    print(f"🗑️ Testing delete book ID: {book_id}")
    response = requests.delete(
        f"{BASE_URL}/api/books/{book_id}",
        headers=get_auth_headers()
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "successfully deleted" in result["message"]
    print("✅ Book deleted successfully")

def test_pagination():
    """Test pagination"""
    print("📄 Testing pagination...")
    
    # Add multiple books first
    books_to_add = [
        {"title": "1984", "author": "George Orwell", "published_date": "1949-06-08", "number_of_pages": 328},
        {"title": "To Kill a Mockingbird", "author": "Harper Lee", "published_date": "1960-07-11", "number_of_pages": 281},
        {"title": "Pride and Prejudice", "author": "Jane Austen", "published_date": "1813-01-28", "number_of_pages": 432}
    ]
    
    for book_data in books_to_add:
        requests.post(f"{BASE_URL}/api/books", json=book_data, headers=get_auth_headers())
    
    # Test pagination
    response = requests.get(f"{BASE_URL}/api/books?page=1&page_size=2")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["books"]) <= 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    print(f"✅ Pagination working: {len(data['books'])} books on page 1")

def test_authentication_required():
    """Test that authentication is required for write operations"""
    print("🔐 Testing authentication requirements...")
    
    # Try to add book without auth
    book_data = {
        "title": "Unauthorized Book",
        "author": "Anonymous",
        "published_date": "2023-01-01",
        "number_of_pages": 100
    }
    
    response = requests.post(f"{BASE_URL}/api/books", json=book_data)
    assert response.status_code == 401
    print("✅ Authentication correctly required for POST")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting API tests...\n")
    
    try:
        # Basic tests
        test_health_check()
        test_authentication_required()
        
        # CRUD operations
        book_id = test_add_book()
        test_get_all_books()
        test_get_book_by_id(book_id)
        test_update_book(book_id)
        
        # Pagination test
        test_pagination()
        
        # Delete test (do this last)
        test_delete_book(book_id)
        
        print("\n🎉 All tests passed! The API is working correctly.")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection error: Make sure the API server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_all_tests()