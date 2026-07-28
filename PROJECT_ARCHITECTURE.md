# PROJECT ARCHITECTURE

**Project:** AI-Powered Smart Student Learning Assistant  
**Version:** 1.0.0  
**Last Updated:** July 26, 2026

---

## Overview

This document describes the complete system architecture for the AI-Powered Smart Student Learning Assistant, a full-stack academic project implementing advanced RAG (Retrieval-Augmented Generation) and multi-agent AI systems.

---

## Architecture Principles

- **Clean Architecture:** Separation of concerns with distinct layers
- **Microservices-Ready:** Modular design allowing future scaling
- **API-First:** RESTful API design with OpenAPI documentation
- **Security-First:** JWT authentication, role-based access control
- **Scalability:** Horizontal scaling capability with Redis caching
- **Type Safety:** Python type hints and Pydantic validation

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  React + Vite + Tailwind CSS + React Router + TanStack Query  │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST API
┌──────────────────────────▼──────────────────────────────────┐
│                       API Gateway Layer                      │
│                    FastAPI + CORS Middleware                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Business Logic Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Auth Module  │  │  RAG Module  │  │ AI Agent     │      │
│  │              │  │              │  │ Module       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Document     │  │ Learning     │  │ Analytics    │      │
│  │ Processing   │  │ Management   │  │ Module       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      Data Access Layer                       │
│                   SQLAlchemy ORM + Alembic                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼──────┐  ┌────────▼────────┐  ┌─────▼──────┐
│  PostgreSQL  │  │     Redis       │  │   Vector   │
│   Database   │  │     Cache       │  │   Store    │
└──────────────┘  └─────────────────┘  └────────────┘
```

---

## Frontend Architecture

### Technology Stack
- **Framework:** React 18 with Vite
- **Styling:** Tailwind CSS with dark mode support
- **Routing:** React Router v6
- **State Management:** TanStack Query (React Query)
- **HTTP Client:** Axios with interceptors
- **Charts:** Recharts for analytics visualization
- **Icons:** Lucide React

### Directory Structure
```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/           # Page-level components
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx
│   │   ├── StudentDashboard.jsx
│   │   ├── FacultyDashboard.jsx
│   │   └── AdminDashboard.jsx
│   ├── services/        # API service layer
│   │   └── api.js       # Axios instance with interceptors
│   ├── hooks/           # Custom React hooks
│   ├── utils/           # Utility functions
│   ├── router.jsx       # Route configuration
│   ├── App.jsx          # Root component
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles with Tailwind
├── public/              # Static assets
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

### Component Architecture
- **Page Components:** Route-level components (Login, Dashboard, etc.)
- **Container Components:** Stateful components managing data fetching
- **Presentational Components:** Stateless UI components
- **Service Layer:** Centralized API calls with Axios

### State Management Strategy
- **Server State:** TanStack Query for API data caching and synchronization
- **Local State:** React useState/useReducer for component state
- **Global State:** React Context for authentication state

---

## Backend Architecture

### Technology Stack
- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Validation:** Pydantic v2
- **Authentication:** JWT (python-jose)
- **Password Hashing:** Passlib with bcrypt
- **AI Frameworks:** LangChain, LangGraph
- **AI API:** Google Gemini API

### Directory Structure
```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── endpoints/
│   │   │   └── auth.py  # Authentication endpoints
│   │   └── deps.py      # API router aggregation
│   ├── core/            # Core configuration
│   │   ├── config.py    # Settings management
│   │   └── security.py  # Security utilities
│   ├── models/          # SQLAlchemy models
│   │   └── user.py      # User model
│   ├── schemas/         # Pydantic schemas
│   │   └── user.py      # User schemas
│   ├── services/        # Business logic layer
│   ├── db/              # Database configuration
│   │   └── database.py  # Database session management
│   └── auth/            # Authentication utilities
│       └── dependencies.py  # Auth dependencies
├── alembic/             # Database migrations
│   ├── versions/        # Migration files
│   ├── env.py           # Alembic environment
│   └── script.py.mako   # Migration template
├── requirements.txt
├── alembic.ini
├── pytest.ini
└── main.py              # Application entry point
```

### Layer Architecture

#### 1. **API Layer** (`app/api/`)
- RESTful endpoints using FastAPI
- Request/response validation with Pydantic
- Dependency injection for database sessions
- Role-based access control

#### 2. **Core Layer** (`app/core/`)
- Configuration management with Pydantic Settings
- Security utilities (JWT, password hashing)
- Environment variable handling

#### 3. **Models Layer** (`app/models/`)
- SQLAlchemy ORM models
- Database table definitions
- Relationships and constraints

#### 4. **Schemas Layer** (`app/schemas/`)
- Pydantic models for validation
- Request/response schemas
- Data serialization/deserialization

#### 5. **Services Layer** (`app/services/`)
- Business logic implementation
- External API integrations
- Complex operations orchestration

#### 6. **Database Layer** (`app/db/`)
- Database connection management
- Session handling
- Transaction management

#### 7. **Auth Layer** (`app/auth/`)
- Authentication dependencies
- Authorization decorators
- User context management

---

## Database Architecture

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR NOT NULL,
    hashed_password VARCHAR NOT NULL,
    role VARCHAR NOT NULL DEFAULT 'student',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Planned Tables (To be implemented)
- `documents` - Document storage and metadata
- `document_chunks` - Text chunks for RAG
- `embeddings` - Vector embeddings
- `courses` - Course information
- `assignments` - Assignment details
- `notes` - Study notes
- `todos` - To-do items
- `flashcards` - Flashcard data
- `quizzes` - Quiz questions
- `analytics` - Learning analytics
- `audit_logs` - System audit trail

### Migration Strategy
- **Alembic** for version-controlled migrations
- **Auto-generation** from SQLAlchemy models
- **Rollback support** for all migrations
- **Seed data** for initial users

---

## Advanced RAG Architecture

### RAG Pipeline Components

#### 1. **Document Processing Pipeline**
```
Document Upload → Format Detection → Text Extraction → OCR (if needed)
→ Text Cleaning → Chunking → Metadata Extraction → Embedding Generation
→ Vector Storage
```

#### 2. **Query Processing Pipeline**
```
User Query → Query Rewriting → BM25 Search → Vector Search
→ Hybrid Retrieval → Cross-Encoder Reranking → Context Compression
→ Citation Generation → Answer Generation
```

### RAG Components
- **Text Extraction:** Support for PDF, DOCX, PPTX, XLSX, TXT, Markdown
- **OCR:** Image-to-text conversion
- **Chunking:** Intelligent document segmentation
- **Embedding:** Vector representation generation
- **BM25:** Keyword-based retrieval
- **Vector Search:** Semantic similarity search
- **Hybrid Retrieval:** Combined BM25 + vector search
- **Reranking:** Cross-encoder result refinement
- **Context Compression:** Context optimization
- **Citation Generation:** Source attribution

---

## Multi-Agent AI Architecture

### Agent System Design

#### Agent Hierarchy
```
Supervisor Agent (Task Router)
    ├── Academic Agent (Academic queries)
    ├── RAG Agent (Document-based queries)
    ├── Coding Agent (Programming assistance)
    ├── Quiz Agent (Quiz generation)
    ├── Study Planner Agent (Learning schedules)
    └── Analytics Agent (Learning analytics)
```

### Agent Components
- **Supervisor Agent:** Routes queries to appropriate specialized agents
- **Academic Agent:** Handles general academic questions
- **RAG Agent:** Manages document retrieval and answer generation
- **Coding Agent:** Provides programming assistance
- **Quiz Agent:** Generates adaptive quizzes
- **Study Planner Agent:** Creates personalized study schedules
- **Analytics Agent:** Analyzes learning patterns and provides insights

### Agent Orchestration
- **LangGraph** for agent workflow management
- **LangChain** for agent implementation
- **Gemini API** for AI responses
- **State Management:** Shared context across agents

---

## Security Architecture

### Authentication Flow
```
1. User submits credentials
2. Server validates credentials
3. Server generates JWT token
4. Client stores token
5. Client includes token in requests
6. Server validates token on each request
7. Server extracts user context from token
```

### Authorization Model
- **Role-Based Access Control (RBAC)**
- **Three Roles:** Student, Faculty, Admin
- **Endpoint Protection:** Role-based route guards
- **Resource-Level Security:** User-specific data access

### Security Measures
- **Password Hashing:** bcrypt with salt
- **JWT Tokens:** Short-lived access tokens
- **HTTPS:** Encrypted communication (production)
- **CORS:** Configured allowed origins
- **Input Validation:** Pydantic schema validation
- **SQL Injection Prevention:** SQLAlchemy ORM
- **XSS Prevention:** React escaping

---

## Caching Architecture

### Redis Caching Strategy
- **Session Storage:** User session data
- **Query Caching:** Frequent query results
- **API Response Caching:** External API responses
- **Rate Limiting:** Request throttling

### Cache Invalidation
- **Time-Based:** TTL expiration
- **Event-Based:** Data change triggers
- **Manual:** Admin-controlled invalidation

---

## API Architecture

### RESTful API Design
- **Resource-Based URLs:** `/api/{resource}/{id}`
- **HTTP Methods:** GET, POST, PUT, DELETE, PATCH
- **Status Codes:** Proper HTTP status codes
- **Error Handling:** Consistent error responses
- **Pagination:** Cursor-based pagination
- **Filtering:** Query parameter filtering
- **Sorting:** Configurable sorting

### API Endpoints Structure
```
/api
├── /auth
│   ├── POST /register
│   └── POST /login
├── /students
│   ├── GET /dashboard
│   ├── POST /documents
│   └── POST /questions
├── /faculty
│   ├── GET /dashboard
│   ├── POST /courses
│   └── POST /assignments
└── /admin
    ├── GET /dashboard
    ├── GET /users
    └── GET /statistics
```

---

## Testing Architecture

### Testing Strategy
- **Unit Tests:** Individual component testing
- **Integration Tests:** API endpoint testing
- **End-to-End Tests:** Full workflow testing

### Backend Testing
- **Framework:** pytest
- **Database:** SQLite test database
- **Fixtures:** Test data setup
- **Coverage:** Code coverage reporting

### Frontend Testing
- **Framework:** Vitest
- **Testing Library:** React Testing Library
- **Mocking:** API response mocking
- **Coverage:** Component coverage reporting

---

## Deployment Architecture

### Development Environment
- **Frontend:** Vite dev server (port 5173)
- **Backend:** Uvicorn server (port 8000)
- **Database:** PostgreSQL local instance
- **Cache:** Redis local instance

### Production Considerations
- **Frontend:** Static file serving (Nginx)
- **Backend:** Gunicorn/Uvicorn workers
- **Database:** PostgreSQL with connection pooling
- **Cache:** Redis with persistence
- **Load Balancer:** Nginx reverse proxy
- **SSL:** HTTPS termination

---

## Monitoring and Logging

### Logging Strategy
- **Structured Logging:** JSON-formatted logs
- **Log Levels:** DEBUG, INFO, WARNING, ERROR
- **Log Rotation:** Automatic log file rotation
- **Centralized Logging:** Log aggregation (future)

### Monitoring Metrics
- **API Response Times:** Endpoint performance
- **Error Rates:** Failure tracking
- **User Activity:** Usage analytics
- **System Health:** Resource utilization

---

## Future Architecture Enhancements

### Scalability
- **Horizontal Scaling:** Multiple backend instances
- **Database Sharding:** Data distribution
- **CDN Integration:** Static asset delivery
- **Message Queue:** Async task processing

### Performance
- **Database Indexing:** Query optimization
- **Caching Layers:** Multi-level caching
- **Connection Pooling:** Database connection reuse
- **Lazy Loading:** On-demand data loading

### Features
- **WebSocket Support:** Real-time updates
- **File Storage:** S3 integration
- **Email Notifications:** SMTP integration
- **Webhook System:** Event notifications

---

## Technology Rationale

### Frontend Choices
- **React:** Large ecosystem, component reusability
- **Vite:** Fast development server, optimized builds
- **Tailwind CSS:** Utility-first, rapid UI development
- **TanStack Query:** Efficient data fetching and caching
- **Recharts:** Declarative charting library

### Backend Choices
- **FastAPI:** High performance, automatic API docs
- **SQLAlchemy:** Mature ORM, database agnostic
- **Alembic:** Reliable migration tool
- **Pydantic:** Data validation, type safety
- **LangChain:** AI framework flexibility
- **LangGraph:** Agent orchestration

### Database Choices
- **PostgreSQL:** ACID compliance, JSON support
- **Redis:** Fast in-memory caching
- **Vector Store:** (To be selected) for embeddings

---

## Architecture Diagrams

### System Flow Diagram
```
User → Frontend → API Gateway → Business Logic → Data Layer → Database
                      ↓                      ↓
                   Redis Cache         Vector Store
                      ↓
                 AI Services (Gemini API)
```

### Authentication Flow
```
Client → /api/auth/login → Validate Credentials → Generate JWT → Return Token
Client → /api/protected → Validate JWT → Extract User → Process Request
```

### RAG Query Flow
```
User Query → Query Rewriting → BM25 Search + Vector Search → Reranking
→ Context Compression → AI Generation → Citation Generation → Response
```

---

## Conclusion

This architecture provides a solid foundation for the AI-Powered Smart Student Learning Assistant, balancing current requirements with future scalability needs. The clean architecture principles ensure maintainability, while the modular design allows for incremental feature development.
