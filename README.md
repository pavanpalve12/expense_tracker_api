# Expense Tracker API

A clean, modular, production-ready **FastAPI backend** for managing users, authentication, JWT access tokens, refresh tokens, and expense tracking with filtering, sorting, and soft deletion.

This project is built with best practices for API design, security, database modeling, and token-based authentication.

---
# Project Link
[https://roadmap.sh/projects/expense-tracker-api](https://roadmap.sh/projects/expense-tracker-api)

## 🚀 Features

### ✅ User Authentication
- User registration & login
- Password hashing using `bcrypt`
- JWT **access token** (15-minute expiry)
- JWT-based **refresh token** system (30-day expiry)
- Secure hashing of refresh tokens (HMAC-SHA256)
- Token rotation
- Replay detection
- Logout (revokes tokens)
- `/users/me` endpoint for retrieving the authenticated user

### ✅ Expense Management
- Create, list, update, replace, and soft-delete expenses
- Advanced filtering:
  - category
  - date range
  - duration (week, month, quarter)
  - amount (gt / lt)
- Sorting by any column (ASC/DESC)
- Data isolation: each user sees only their own expenses

### ✅ Database
- SQLAlchemy ORM models
- Alembic migrations
- Relationships:
  - `User 1 → * Expenses`
  - `User 1 → * RefreshTokens`
- SQLite (dev) / PostgreSQL ready

### ✅ API Documentation
- Automatic interactive docs via **Swagger UI** (`/docs`)
- `/users/token` OAuth2 login support for testing inside Swagger
- CORS enabled for local development

---

## 🛠 Tech Stack

- **FastAPI**
- **SQLAlchemy ORM**
- **Alembic** migrations
- **PyJWT**
- **bcrypt**
- **SQLite / PostgreSQL**
- **Pydantic v2**

---


Server:
- Verifies refresh token
- Rotates refresh token
- Issues new access + refresh token pair

### 4️⃣ Logout
- Marks refresh tokens as revoked
- Any attempt to reuse old refresh token triggers replay detection

---

## 📘 API Endpoints

### 🔑 Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users/signup` | Register user |
| POST | `/users/login` | Login with JSON body |
| POST | `/users/token` | OAuth2 login for Swagger |
| POST | `/users/token/refresh` | Get new access + refresh tokens |
| POST | `/users/logout` | Logout & revoke tokens |
| GET | `/users/me` | Get authenticated user |

---

### 💰 Expenses
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/{user_id}/expenses` | List expenses with filters & sorting |
| POST | `/users/{user_id}/expenses` | Add expense |
| PUT | `/users/{user_id}/expenses/{expense_id}` | Replace expense |
| PATCH | `/users/{user_id}/expenses/{expense_id}` | Update partial fields |
| DELETE | `/users/{user_id}/expenses/{expense_id}` | Soft delete expense |

---

## 🧪 Testing With Curl

### Login
```bash
curl -X POST http://127.0.0.1:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secret123"}'


---

If you'd like, I can also generate:  
✅ A **CONTRIBUTING.md**  
✅ A **Postman collection**  
✅ A **diagram (flow + ERD)** in markdown  
Just tell me.


