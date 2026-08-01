# API Documentation

**Project:** AI-Powered Smart Student Learning Assistant  
**Version:** 1.0.0  
**Last Updated:** July 30, 2026

---

## Overview

This document provides comprehensive documentation for all API endpoints in the AI-Powered Smart Student Learning Assistant. The API is built using FastAPI and follows RESTful principles.

### Base URL
- **Development:** `http://localhost:8000/api`
- **Production:** `https://your-domain.com/api`

### Authentication
All protected endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Response Format
All responses follow this structure:
```json
{
  "data": { ... },
  "message": "Success message",
  "status_code": 200
}
```

Error responses:
```json
{
  "detail": "Error message",
  "status_code": 400,
  "type": "app_error"
}
```

---

## PHASE 11: Quiz APIs

### Question Generation

#### Generate AI Questions
```http
POST /api/quizzes/generate-questions
```

**Description:** Generate quiz questions using AI (Gemini API)

**Query Parameters:**
- `topic` (string, required): Topic to generate questions for
- `difficulty` (enum, optional): Question difficulty (easy, medium, hard) - default: medium
- `question_count` (integer, optional): Number of questions (1-20) - default: 5
- `question_type` (enum, optional): Type of questions - default: multiple_choice

**Authentication:** Required

**Example Request:**
```bash
GET /api/quizzes/generate-questions?topic=Python%20Programming&difficulty=medium&question_count=5
```

**Example Response:**
```json
{
  "topic": "Python Programming",
  "difficulty": "medium",
  "question_type": "multiple_choice",
  "questions": [
    {
      "question_text": "What is Python?",
      "question_type": "multiple_choice",
      "options": "[\"A language\", \"A snake\", \"A tool\", \"A framework\"]",
      "correct_answer": "0",
      "points": 1
    }
  ]
}
```

---

### Question Bank Management

#### Create Question Bank
```http
POST /api/quizzes/question-bank
```

**Description:** Create a reusable question bank for a topic

**Authentication:** Required

**Request Body:**
```json
{
  "topic": "Python Programming",
  "description": "Basic Python concepts",
  "difficulty": "medium",
  "questions": [
    {
      "question_text": "What is Python?",
      "question_type": "multiple_choice",
      "options": ["A language", "A snake", "A tool", "A framework"],
      "correct_answer": "0",
      "points": 1,
      "order": 0
    }
  ]
}
```

**Example Response:**
```json
{
  "id": 1,
  "title": "Question Bank: Python Programming",
  "description": "Basic Python concepts",
  "difficulty": "medium",
  "created_by": 1,
  "is_active": true,
  "created_at": "2026-07-30T00:00:00Z"
}
```

#### Get Question Banks
```http
GET /api/quizzes/question-bank
```

**Description:** Get all question banks for the current user

**Query Parameters:**
- `topic` (string, optional): Filter by topic

**Authentication:** Required

#### Get Question Bank Questions
```http
GET /api/quizzes/question-bank/{bank_id}/questions
```

**Description:** Get all questions from a specific question bank

**Authentication:** Required

---

### Adaptive Learning

#### Generate Adaptive Quiz
```http
POST /api/quizzes/adaptive
```

**Description:** Generate an adaptive quiz based on student performance history

**Authentication:** Required

**Request Body:**
```json
{
  "topic": "Python Programming",
  "question_count": 10,
  "time_limit": 30
}
```

**Example Response:**
```json
{
  "id": 1,
  "title": "Adaptive Quiz: Python Programming",
  "description": "Adaptive quiz for Python Programming based on your performance",
  "difficulty": "medium",
  "time_limit": 30,
  "questions": [...]
}
```

---

### Quiz History & Analytics

#### Get Quiz History
```http
GET /api/quizzes/history
```

**Description:** Get student's quiz attempt history with pagination

**Query Parameters:**
- `limit` (integer, optional): Number of results (1-100) - default: 10
- `offset` (integer, optional): Offset for pagination - default: 0

**Authentication:** Required

**Example Response:**
```json
{
  "attempts": [...],
  "total_attempts": 25,
  "average_score": 78.5,
  "completed_count": 20
}
```

#### Get Quiz Performance Analytics
```http
GET /api/quizzes/performance-analytics
```

**Description:** Get detailed quiz performance analytics over time

**Query Parameters:**
- `days` (integer, optional): Period in days (1-365) - default: 30

**Authentication:** Required

**Example Response:**
```json
{
  "period_days": 30,
  "total_attempts": 15,
  "average_score": 82.3,
  "highest_score": 95.0,
  "lowest_score": 65.0,
  "improvement_rate": 12.5,
  "difficulty_distribution": {
    "easy": 5,
    "medium": 8,
    "hard": 2
  },
  "topic_performance": [...]
}
```

---

## PHASE 12: Flashcard APIs

### Topic Grouping

#### Get Deck Statistics
```http
GET /api/flashcards/decks/statistics
```

**Description:** Get statistics for each flashcard deck/topic

**Authentication:** Required

**Example Response:**
```json
[
  {
    "deck_name": "Python Programming",
    "total_cards": 50,
    "new_cards": 10,
    "learning_cards": 15,
    "review_cards": 20,
    "mastered_cards": 5,
    "due_for_review": 15
  }
]
```

#### Update Deck Name
```http
PUT /api/flashcards/decks/{deck_name}
```

**Description:** Rename a deck/topic

**Query Parameters:**
- `new_deck_name` (string, required): New name for the deck

**Authentication:** Required

---

### Scheduling

#### Get Study Schedule
```http
GET /api/flashcards/schedule
```

**Description:** Get study schedule showing cards due for review in the next N days

**Query Parameters:**
- `days` (integer, optional): Number of days to schedule (1-30) - default: 7

**Authentication:** Required

**Example Response:**
```json
{
  "period_days": 7,
  "start_date": "2026-07-30",
  "end_date": "2026-08-05",
  "total_due_cards": 25,
  "daily_schedule": {
    "2026-07-30": {
      "date": "2026-07-30",
      "due_count": 5,
      "cards": [...]
    },
    ...
  }
}
```

---

### Progress Tracking

#### Get Flashcard Progress
```http
GET /api/flashcards/progress
```

**Description:** Get overall flashcard learning progress

**Query Parameters:**
- `days` (integer, optional): Period in days (1-365) - default: 30

**Authentication:** Required

**Example Response:**
```json
{
  "total_cards": 100,
  "mastered_cards": 30,
  "learning_cards": 40,
  "review_cards": 25,
  "new_cards": 5,
  "mastery_percentage": 30.0,
  "total_reviews_period": 150,
  "average_rating": 4.2,
  "retention_rate": 85.0
}
```

---

### Batch Operations

#### Create Flashcard Batch
```http
POST /api/flashcards/batch
```

**Description:** Create multiple flashcards at once

**Authentication:** Required

**Request Body:**
```json
[
  {
    "front": "What is Python?",
    "back": "Python is a high-level programming language",
    "deck_name": "Programming"
  },
  ...
]
```

---

## PHASE 13: Analytics APIs

### Dashboard Overview

#### Get Dashboard Overview
```http
GET /api/learning/dashboard
```

**Description:** Get comprehensive dashboard overview with all key metrics

**Authentication:** Required

**Example Response:**
```json
{
  "learning_metrics": {
    "total_topics": 15,
    "average_mastery": 72.5,
    "total_time_spent_hours": 45.5,
    "topics_mastered": 8
  },
  "quiz_metrics": {
    "total_attempts": 25,
    "average_score": 78.5,
    "completed_count": 20
  },
  "flashcard_metrics": {
    "total_cards": 100,
    "mastered_cards": 30,
    "mastery_percentage": 30.0
  },
  "weak_topics": [...],
  "recent_activity": {...}
}
```

---

### Comprehensive Analytics

#### Get Comprehensive Analytics
```http
GET /api/learning/comprehensive
```

**Description:** Get comprehensive analytics for a specified time period

**Query Parameters:**
- `days` (integer, optional): Period in days (1-365) - default: 30

**Authentication:** Required

**Example Response:**
```json
{
  "period_days": 30,
  "total_study_time_hours": 35.5,
  "topics_studied": 12,
  "quizzes_completed": 8,
  "flashcards_reviewed": 150,
  "average_quiz_score": 82.3,
  "completion_rate": 85.0,
  "study_streak": 7
}
```

---

### Learning Trends

#### Get Learning Trends
```http
GET /api/learning/trends
```

**Description:** Get learning trends over time with daily breakdown

**Query Parameters:**
- `days` (integer, optional): Period in days (7-365) - default: 30

**Authentication:** Required

**Example Response:**
```json
{
  "period_days": 30,
  "total_activity": 145,
  "average_daily_activity": 4.83,
  "most_active_day": "2026-07-15",
  "daily_breakdown": {
    "2026-07-30": {
      "date": "2026-07-30",
      "progress_updates": 3,
      "quizzes_completed": 1,
      "flashcards_reviewed": 10
    },
    ...
  }
}
```

---

### Study Statistics

#### Get Study Statistics
```http
GET /api/learning/statistics
```

**Description:** Get detailed study statistics

**Authentication:** Required

**Example Response:**
```json
{
  "overall_statistics": {
    "total_topics_studied": 15,
    "total_quizzes_taken": 25,
    "total_flashcards_created": 100
  },
  "time_statistics": {
    "total_study_time_hours": 45.5,
    "average_time_per_topic_minutes": 182.0
  },
  "performance_statistics": {
    "average_quiz_score": 78.5,
    "highest_quiz_score": 95.0,
    "lowest_quiz_score": 65.0
  }
}
```

---

### Topic Performance

#### Get Topic Performance
```http
GET /api/learning/topic-performance
```

**Description:** Get performance breakdown by topic

**Authentication:** Required

**Example Response:**
```json
[
  {
    "topic": "Python Programming",
    "mastery_level": 85.0,
    "time_spent_minutes": 300,
    "last_studied": "2026-07-30T10:30:00Z",
    "study_frequency": 8
  },
  ...
]
```

---

### Time Analytics

#### Get Time Spent Analytics
```http
GET /api/learning/time-analytics
```

**Description:** Get detailed time spent analytics by topic and day

**Query Parameters:**
- `days` (integer, optional): Period in days (1-365) - default: 30

**Authentication:** Required

**Example Response:**
```json
{
  "period_days": 30,
  "total_time_spent_hours": 35.5,
  "time_by_topic": {
    "Python Programming": 15.5,
    "Data Structures": 10.0,
    "Algorithms": 10.0
  },
  "daily_time_spent_hours": {
    "2026-07-30": 2.5,
    "2026-07-29": 1.5
  },
  "average_daily_hours": 1.18
}
```

---

## PHASE 14: API Features

### Validation

All endpoints implement comprehensive validation using Pydantic schemas:

- **Type Validation:** Ensures data types are correct
- **Range Validation:** Validates numeric ranges (e.g., question_count: 1-20)
- **Enum Validation:** Ensures enum values are valid
- **Required Fields:** Validates required fields are present
- **Format Validation:** Validates data formats (dates, emails, etc.)

### Error Handling

The API uses custom exception handlers for consistent error responses:

- **400 Bad Request:** Invalid input data
- **401 Unauthorized:** Missing or invalid authentication
- **403 Forbidden:** Insufficient permissions
- **404 Not Found:** Resource not found
- **409 Conflict:** Resource conflict (e.g., duplicate)
- **422 Unprocessable Entity:** Validation error
- **503 Service Unavailable:** Service temporarily unavailable

### Authentication & Authorization

- **JWT Authentication:** Required for all protected endpoints
- **Role-Based Access Control:** Different access levels for Student, Faculty, Admin
- **Resource Ownership:** Users can only access their own resources
- **Admin Override:** Admins can access all resources

### API Documentation

Interactive API documentation is available at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## Rate Limiting

To prevent abuse, the API implements rate limiting:

- **Anonymous Requests:** 100 requests/hour
- **Authenticated Requests:** 1000 requests/hour
- **AI Generation Endpoints:** 50 requests/hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1690742400
```

---

## Testing

### Example cURL Commands

**Generate Questions:**
```bash
curl -X GET "http://localhost:8000/api/quizzes/generate-questions?topic=Python&difficulty=medium&question_count=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Create Question Bank:**
```bash
curl -X POST "http://localhost:8000/api/quizzes/question-bank" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Python","questions":[...]}'
```

**Get Dashboard:**
```bash
curl -X GET "http://localhost:8000/api/learning/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Changelog

### Version 1.0.0 (July 30, 2026)
- Initial release of Phases 11-14 APIs
- Quiz question generation with AI
- Question bank management
- Adaptive quiz generation
- Flashcard topic grouping and scheduling
- Comprehensive analytics dashboard
- Learning trends and statistics
- Enhanced validation and error handling
- Interactive API documentation

---

## Support

For API support and issues, please contact the development team or refer to the project documentation.
