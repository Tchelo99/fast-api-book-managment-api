# FastAPI Book Management API
# Complete implementation with authentication, pagination, and database

from fastapi import FastAPI, HTTPException, Depends, status, Query, Path
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List, Optional
import secrets
import uvicorn

# Database Configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./books.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class BookDB(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    published_date = Column(Date)
    number_of_pages = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Enhanced Pydantic Models with Examples
class BookBase(BaseModel):
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=200, 
        description="Title of the book",
        example="The Great Gatsby"
    )
    author: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Author of the book",
        example="F. Scott Fitzgerald"
    )
    published_date: date = Field(
        ..., 
        description="Publication date in YYYY-MM-DD format",
        example="1925-04-10"
    )
    number_of_pages: int = Field(
        ..., 
        gt=0, 
        description="Number of pages in the book (must be positive)",
        example=180
    )

class BookCreate(BookBase):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "The Great Gatsby",
                    "author": "F. Scott Fitzgerald",
                    "published_date": "1925-04-10",
                    "number_of_pages": 180
                },
                {
                    "title": "1984",
                    "author": "George Orwell",
                    "published_date": "1949-06-08",
                    "number_of_pages": 328
                }
            ]
        }
    }

class BookUpdate(BaseModel):
    title: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=200,
        description="Updated title of the book",
        example="The Great Gatsby - Updated Edition"
    )
    author: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=100,
        description="Updated author of the book",
        example="F. Scott Fitzgerald"
    )
    published_date: Optional[date] = Field(
        None,
        description="Updated publication date",
        example="1925-04-10"
    )
    number_of_pages: Optional[int] = Field(
        None, 
        gt=0,
        description="Updated number of pages",
        example=200
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "The Great Gatsby - Updated Edition",
                    "number_of_pages": 200
                },
                {
                    "author": "George Orwell (Updated)",
                    "published_date": "1949-06-08"
                }
            ]
        }
    }

class Book(BookBase):
    id: int = Field(..., description="Unique identifier for the book", example=1)
    created_at: datetime = Field(..., description="Timestamp when the book was added")
    updated_at: datetime = Field(..., description="Timestamp when the book was last updated")
    
    class Config:
        from_attributes = True

class BooksResponse(BaseModel):
    books: List[Book] = Field(..., description="List of books")
    total: int = Field(..., description="Total number of books in the database", example=25)
    page: int = Field(..., description="Current page number", example=1)
    page_size: int = Field(..., description="Number of items per page", example=10)
    total_pages: int = Field(..., description="Total number of pages", example=3)

class MessageResponse(BaseModel):
    message: str = Field(..., description="Response message", example="Operation completed successfully")

# FastAPI App with Enhanced Swagger Documentation
app = FastAPI(
    title="📚 Book Management API",
    description="""
## Book Management System

A comprehensive RESTful API for managing a collection of books with authentication and pagination.

### Features
* **Complete CRUD Operations** - Create, Read, Update, Delete books
* **Authentication** - HTTP Basic Authentication for write operations
* **Pagination** - Efficient book listing with customizable page sizes
* **Data Validation** - Comprehensive input validation using Pydantic
* **Error Handling** - Detailed error responses with proper HTTP status codes

### Authentication
- **Protected Endpoints**: POST, PUT, DELETE operations require authentication
- **Public Endpoints**: GET operations are publicly accessible
- **Credentials**: Use `admin/password123` or `user/userpass` for testing

### API Versioning
Current version: **v1.0.0**
    """,
    version="1.0.0",
    contact={
        "name": "Book Management API Support",
        "url": "https://github.com/your-repo/book-management-api",
        "email": "support@bookapi.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    terms_of_service="https://your-domain.com/terms",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Health",
            "description": "Health check and system status endpoints"
        },
        {
            "name": "Books",
            "description": "Operations for managing books. **Authentication required** for POST, PUT, DELETE operations."
        },
        {
            "name": "Info",
            "description": "General information and welcome endpoints"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBasic()

# Simple authentication (in production, use proper user management)
VALID_CREDENTIALS = {
    "admin": "password123",
    "user": "userpass"
}

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    """Authenticate user with basic auth"""
    username = credentials.username
    password = credentials.password
    
    if username not in VALID_CREDENTIALS or not secrets.compare_digest(
        password, VALID_CREDENTIALS[username]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return username

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD Operations
def get_book_by_id(db: Session, book_id: int):
    return db.query(BookDB).filter(BookDB.id == book_id).first()

def get_books(db: Session, skip: int = 0, limit: int = 10):
    total = db.query(BookDB).count()
    books = db.query(BookDB).offset(skip).limit(limit).all()
    return books, total

def create_book(db: Session, book: BookCreate):
    db_book = BookDB(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def update_book(db: Session, book_id: int, book_update: BookUpdate):
    db_book = get_book_by_id(db, book_id)
    if not db_book:
        return None
    
    update_data = book_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    db_book.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int):
    db_book = get_book_by_id(db, book_id)
    if db_book:
        db.delete(db_book)
        db.commit()
        return True
    return False

# Enhanced API Endpoints with Comprehensive Swagger Documentation

@app.get("/", 
         response_model=MessageResponse,
         tags=["Info"],
         summary="Welcome Message",
         description="Get a welcome message from the Book Management API")
async def root():
    """
    ## Welcome Endpoint
    
    Returns a welcome message with information about the API.
    
    - **No authentication required**
    - **Returns**: Welcome message with link to documentation
    """
    return {"message": "Welcome to the Book Management API! Visit /docs for API documentation."}

@app.post("/api/books", 
          response_model=Book, 
          status_code=status.HTTP_201_CREATED,
          tags=["Books"],
          summary="Add a New Book",
          description="Create a new book in the collection",
          responses={
              201: {
                  "description": "Book successfully created",
                  "content": {
                      "application/json": {
                          "example": {
                              "id": 1,
                              "title": "The Great Gatsby",
                              "author": "F. Scott Fitzgerald",
                              "published_date": "1925-04-10",
                              "number_of_pages": 180,
                              "created_at": "2025-05-25T10:30:00.123456",
                              "updated_at": "2025-05-25T10:30:00.123456"
                          }
                      }
                  }
              },
              401: {
                  "description": "Authentication required",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Invalid credentials"}
                      }
                  }
              },
              422: {
                  "description": "Validation error",
                  "content": {
                      "application/json": {
                          "example": {
                              "detail": [
                                  {
                                      "loc": ["body", "number_of_pages"],
                                      "msg": "ensure this value is greater than 0",
                                      "type": "value_error.number.not_gt"
                                  }
                              ]
                          }
                      }
                  }
              }
          })
async def add_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(authenticate)
):
    """
    ## Add a New Book
    
    Create a new book in the collection with the provided details.
    
    - **Authentication**: Required (HTTP Basic Auth)
    - **Permissions**: Any authenticated user can add books
    - **Validation**: All fields are required and validated
    
    ### Request Body
    - **title**: Book title (1-200 characters)
    - **author**: Book author (1-100 characters)  
    - **published_date**: Publication date (YYYY-MM-DD format)
    - **number_of_pages**: Number of pages (positive integer)
    
    ### Returns
    - **201**: Book successfully created with generated ID and timestamps
    - **401**: Authentication required
    - **422**: Validation errors in request data
    """
    return create_book(db, book)

@app.get("/api/books", 
         response_model=BooksResponse,
         tags=["Books"],
         summary="Get All Books",
         description="Retrieve a paginated list of all books",
         responses={
             200: {
                 "description": "List of books with pagination info",
                 "content": {
                     "application/json": {
                         "example": {
                             "books": [
                                 {
                                     "id": 1,
                                     "title": "The Great Gatsby",
                                     "author": "F. Scott Fitzgerald",
                                     "published_date": "1925-04-10",
                                     "number_of_pages": 180,
                                     "created_at": "2025-05-25T10:30:00.123456",
                                     "updated_at": "2025-05-25T10:30:00.123456"
                                 }
                             ],
                             "total": 1,
                             "page": 1,
                             "page_size": 10,
                             "total_pages": 1
                         }
                     }
                 }
             }
         })
async def get_all_books(
    page: int = Query(1, ge=1, description="Page number (starts from 1)", example=1),
    page_size: int = Query(10, ge=1, le=100, description="Number of books per page (1-100)", example=10),
    db: Session = Depends(get_db)
):
    """
    ## Get All Books (Paginated)
    
    Retrieve a paginated list of all books in the collection.
    
    - **Authentication**: Not required (public endpoint)
    - **Pagination**: Supports page and page_size parameters
    - **Default**: Returns page 1 with 10 books per page
    
    ### Query Parameters
    - **page**: Page number (minimum: 1, default: 1)
    - **page_size**: Items per page (minimum: 1, maximum: 100, default: 10)
    
    ### Returns
    - **books**: Array of book objects
    - **total**: Total number of books in database
    - **page**: Current page number
    - **page_size**: Number of items per page
    - **total_pages**: Total number of pages available
    """
    skip = (page - 1) * page_size
    books, total = get_books(db, skip=skip, limit=page_size)
    total_pages = (total + page_size - 1) // page_size
    
    return BooksResponse(
        books=books,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@app.get("/api/books/{book_id}", 
         response_model=Book,
         tags=["Books"],
         summary="Get Specific Book",
         description="Retrieve details of a specific book by ID",
         responses={
             200: {
                 "description": "Book details",
                 "content": {
                     "application/json": {
                         "example": {
                             "id": 1,
                             "title": "The Great Gatsby",
                             "author": "F. Scott Fitzgerald",
                             "published_date": "1925-04-10",
                             "number_of_pages": 180,
                             "created_at": "2025-05-25T10:30:00.123456",
                             "updated_at": "2025-05-25T10:30:00.123456"
                         }
                     }
                 }
             },
             404: {
                 "description": "Book not found",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Book with id 999 not found"}
                     }
                 }
             }
         })
async def get_book(
    book_id: int = Path(..., description="Unique identifier of the book", example=1),
    db: Session = Depends(get_db)
):
    """
    ## Get Book Details
    
    Retrieve detailed information about a specific book.
    
    - **Authentication**: Not required (public endpoint)
    - **Path Parameter**: book_id (integer)
    
    ### Returns
    - **200**: Book details with all fields
    - **404**: Book not found with the specified ID
    """
    book = get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return book

@app.put("/api/books/{book_id}", 
         response_model=Book,
         tags=["Books"],
         summary="Update Book",
         description="Update details of an existing book",
         responses={
             200: {
                 "description": "Book successfully updated",
                 "content": {
                     "application/json": {
                         "example": {
                             "id": 1,
                             "title": "The Great Gatsby - Updated Edition",
                             "author": "F. Scott Fitzgerald",
                             "published_date": "1925-04-10",
                             "number_of_pages": 200,
                             "created_at": "2025-05-25T10:30:00.123456",
                             "updated_at": "2025-05-25T11:15:00.789012"
                         }
                     }
                 }
             },
             401: {
                 "description": "Authentication required",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Invalid credentials"}
                     }
                 }
             },
             404: {
                 "description": "Book not found",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Book with id 999 not found"}
                     }
                 }
             },
             422: {
                 "description": "Validation error",
                 "content": {
                     "application/json": {
                         "example": {
                             "detail": [
                                 {
                                     "loc": ["body", "number_of_pages"],
                                     "msg": "ensure this value is greater than 0",
                                     "type": "value_error.number.not_gt"
                                 }
                             ]
                         }
                     }
                 }
             }
         })
async def update_book_endpoint(
    book_id: int = Path(..., description="Unique identifier of the book to update", example=1),
    book_update: BookUpdate = ...,
    db: Session = Depends(get_db),
    current_user: str = Depends(authenticate)
):
    """
    ## Update Book Details
    
    Update one or more fields of an existing book. Only provide fields that need to be updated.
    
    - **Authentication**: Required (HTTP Basic Auth)
    - **Partial Updates**: Only include fields you want to change
    - **Validation**: Updated fields are validated according to the same rules as creation
    
    ### Path Parameter
    - **book_id**: ID of the book to update
    
    ### Request Body (All fields optional)
    - **title**: Updated book title
    - **author**: Updated author name
    - **published_date**: Updated publication date
    - **number_of_pages**: Updated page count
    
    ### Returns
    - **200**: Book successfully updated with new timestamp
    - **401**: Authentication required
    - **404**: Book not found with specified ID
    - **422**: Validation errors in updated data
    """
    updated_book = update_book(db, book_id, book_update)
    if not updated_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return updated_book

@app.delete("/api/books/{book_id}", 
            response_model=MessageResponse,
            tags=["Books"],
            summary="Delete Book",
            description="Remove a book from the collection",
            responses={
                200: {
                    "description": "Book successfully deleted",
                    "content": {
                        "application/json": {
                            "example": {"message": "Book with id 1 was successfully deleted"}
                        }
                    }
                },
                401: {
                    "description": "Authentication required",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Invalid credentials"}
                        }
                    }
                },
                404: {
                    "description": "Book not found",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Book with id 999 not found"}
                        }
                    }
                }
            })
async def delete_book_endpoint(
    book_id: int = Path(..., description="Unique identifier of the book to delete", example=1),
    db: Session = Depends(get_db),
    current_user: str = Depends(authenticate)
):
    """
    ## Delete Book
    
    Permanently remove a book from the collection.
    
    - **Authentication**: Required (HTTP Basic Auth)
    - **Action**: Irreversible deletion
    - **Path Parameter**: book_id (integer)
    
    ### ⚠️ Warning
    This action cannot be undone. The book will be permanently removed from the database.
    
    ### Returns
    - **200**: Confirmation message of successful deletion
    - **401**: Authentication required
    - **404**: Book not found with specified ID
    """
    if not delete_book(db, book_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return {"message": f"Book with id {book_id} was successfully deleted"}

# Health check endpoint
@app.get("/health", 
         response_model=MessageResponse,
         tags=["Health"],
         summary="Health Check",
         description="Check if the API is running and healthy",
         responses={
             200: {
                 "description": "API is healthy and running",
                 "content": {
                     "application/json": {
                         "example": {"message": "API is healthy"}
                     }
                 }
             }
         })
async def health_check():
    """
    ## Health Check
    
    Simple endpoint to verify that the API is running and responding.
    
    - **Authentication**: Not required
    - **Use Case**: Monitoring, load balancers, CI/CD pipelines
    - **Response**: Always returns 200 if API is running
    
    ### Returns
    - **200**: API is healthy and operational
    """
    return {"message": "API is healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)