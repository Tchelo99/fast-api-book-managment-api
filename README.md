# Book Management API

A RESTful API built with FastAPI for managing a collection of books. This API provides full CRUD operations, authentication, pagination, and automatic API documentation.

## Features

- ✅ **Complete CRUD Operations**: Create, Read, Update, Delete books
- ✅ **Authentication**: Basic HTTP authentication for write operations
- ✅ **Pagination**: Paginated book listings
- ✅ **Database Integration**: SQLite database with SQLAlchemy ORM
- ✅ **Input Validation**: Pydantic models for request/response validation
- ✅ **Comprehensive Swagger Documentation**: Interactive API docs with examples
- ✅ **Auto Documentation**: Enhanced Swagger UI and ReDoc with detailed descriptions
- ✅ **Error Handling**: Comprehensive error responses with proper HTTP status codes
- ✅ **CORS Support**: Cross-origin resource sharing enabled

## Technology Stack

- **FastAPI**: Modern, fast Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight relational database
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running the application

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager


### Option 1: Local Python Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd book-management-api
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host localhost --port 8000
   ```

### Access the Application

- API Base URL: http://localhost:8000
- **Enhanced Swagger UI**: http://localhost:8000/docs (Interactive API documentation with examples)
- Alternative Documentation: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

### Testing the Installation

Run the test script to verify everything works:
```bash
# Install requests if not already installed
pip install requests

# Run tests
python test_api.py
```

### 📚 Using the Swagger Documentation

1. **Open Swagger UI**: http://localhost:8000/docs
2. **Click "Authorize"** (🔒 icon) and enter credentials: `admin` / `password123`
3. **Try any endpoint** by clicking "Try it out" and "Execute"
4. **View detailed examples** and response schemas for all endpoints

## API Endpoints

### Authentication

The API uses HTTP Basic Authentication for write operations (POST, PUT, DELETE). Read operations (GET) are publicly accessible.

**Default Credentials:**
- Username: `admin`, Password: `password123`
- Username: `user`, Password: `userpass`

### Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Welcome message | No |
| GET | `/health` | Health check | No |
| POST | `/api/books` | Add a new book | Yes |
| GET | `/api/books` | Get all books (paginated) | No |
| GET | `/api/books/{id}` | Get specific book | No |
| PUT | `/api/books/{id}` | Update book | Yes |
| DELETE | `/api/books/{id}` | Delete book | Yes |

### Detailed API Documentation

#### 1. Add a New Book
**POST** `/api/books`

**Headers:**
```
Authorization: Basic <base64(username:password)>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "published_date": "1925-04-10",
  "number_of_pages": 180
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "published_date": "1925-04-10",
  "number_of_pages": 180,
  "created_at": "2025-05-25T10:30:00",
  "updated_at": "2025-05-25T10:30:00"
}
```

#### 2. Get All Books (with Pagination)
**GET** `/api/books?page=1&page_size=10`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 10, max: 100)

**Response (200 OK):**
```json
{
  "books": [
    {
      "id": 1,
      "title": "The Great Gatsby",
      "author": "F. Scott Fitzgerald",
      "published_date": "1925-04-10",
      "number_of_pages": 180,
      "created_at": "2025-05-25T10:30:00",
      "updated_at": "2025-05-25T10:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

#### 3. Get Specific Book
**GET** `/api/books/{id}`

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "published_date": "1925-04-10",
  "number_of_pages": 180,
  "created_at": "2025-05-25T10:30:00",
  "updated_at": "2025-05-25T10:30:00"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Book with id 999 not found"
}
```

#### 4. Update Book
**PUT** `/api/books/{id}`

**Headers:**
```
Authorization: Basic <base64(username:password)>
Content-Type: application/json
```

**Request Body (partial update):**
```json
{
  "title": "The Great Gatsby - Updated Edition",
  "number_of_pages": 200
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "The Great Gatsby - Updated Edition",
  "author": "F. Scott Fitzgerald",
  "published_date": "1925-04-10",
  "number_of_pages": 200,
  "created_at": "2025-05-25T10:30:00",
  "updated_at": "2025-05-25T11:15:00"
}
```

#### 5. Delete Book
**DELETE** `/api/books/{id}`

**Headers:**
```
Authorization: Basic <base64(username:password)>
```

**Response (200 OK):**
```json
{
  "message": "Book with id 1 was successfully deleted"
}
```

## Testing the API

### Using curl

1. **Add a book:**
```bash
curl -X POST "http://localhost:8000/api/books" \
  -H "Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984",
    "author": "George Orwell",
    "published_date": "1949-06-08",
    "number_of_pages": 328
  }'
```

2. **Get all books:**
```bash
curl "http://localhost:8000/api/books?page=1&page_size=5"
```

3. **Get specific book:**
```bash
curl "http://localhost:8000/api/books/1"
```

4. **Update a book:**
```bash
curl -X PUT "http://localhost:8000/api/books/1" \
  -H "Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984 - Anniversary Edition"
  }'
```

5. **Delete a book:**
```bash
curl -X DELETE "http://localhost:8000/api/books/1" \
  -H "Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM="
```

### Using the Interactive Documentation

1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter credentials: `admin` / `password123`
4. Try out the endpoints directly in the browser

## Database

The application uses SQLite database (`books.db`) which is created automatically when you run the application for the first time. The database includes:

**Books Table:**
- `id`: Primary key (auto-increment)
- `title`: Book title (string, required)
- `author`: Book author (string, required)
- `published_date`: Publication date (date, required)
- `number_of_pages`: Number of pages (integer, required)
- `created_at`: Record creation timestamp
- `updated_at`: Record last update timestamp

## Project Structure

```
book-management-api/
├── main.py                 # Main application file
├── requirements.txt        # Python dependencies
├── test_api.py            # Test script for API functionality
├── Dockerfile             # Docker container configuration
├── docker-compose.yml     # Docker Compose configuration
├── README.md              # Project documentation
├── data/                  # Data directory (created automatically)
└── books.db              # SQLite database (created automatically)
```

## Development

### Adding New Features

1. **Database Models**: Modify the `BookDB` class in `main.py`
2. **API Models**: Update Pydantic models (`BookCreate`, `BookUpdate`, etc.)
3. **Endpoints**: Add new route functions with appropriate decorators
4. **Documentation**: FastAPI automatically generates documentation from your code

### Environment Variables

You can customize the application using environment variables:

```bash
export DATABASE_URL="sqlite:///./books.db"  # Database connection string
export API_HOST="0.0.0.0"                   # Host to bind to
export API_PORT="8000"                      # Port to bind to
```

## Production Deployment

For production deployment, consider:

1. **Database**: Use PostgreSQL or MySQL instead of SQLite
2. **Authentication**: Implement proper user management with JWT tokens
3. **Security**: Use HTTPS, rate limiting, and input sanitization
4. **Monitoring**: Add logging and health checks
5. **Performance**: Use connection pooling and caching


## Support

For questions or issues, please open an issue in the GitHub repository.