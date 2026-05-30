# JodJam — Backend API

> จดจำ · หนึ่งวัน หนึ่งความทรงจำ

**JodJam** is a daily memory journal API — one entry per day, no backdating, memory is final.

🌐 **Frontend** → [github.com/Bobby9326/JodJam-Frontend](https://github.com/Bobby9326/JodJam-Frontend)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL (Supabase) |
| ORM | SQLModel + SQLAlchemy |
| Auth | Google OAuth 2.0 + JWT |
| Storage | Supabase Storage |
| Runtime | Python 3.13 |
| Deploy | Render |

---

## Project Structure

```
app/
├── core/
│   ├── config.py              # Environment settings
│   ├── database.py            # DB engine & session
│   ├── dependencies.py        # Shared FastAPI dependencies
│   ├── logger.py              # Logger config
│   └── supabase_storage.py    # Storage helper
│
└── modules/
    ├── auths/                 # Google OAuth, JWT, refresh tokens
    ├── memories/              # Daily memory entries
    ├── stats/                 # Statistics & analytics
    └── users/                 # User profile management
```

---

## API Overview

### Auth
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/login/google` | Redirect to Google OAuth |
| GET | `/api/v1/auth/google/callback` | OAuth callback |
| POST | `/api/v1/refresh` | Refresh access token |
| POST | `/api/v1/logout` | Logout & clear cookies |

### Users
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/users/me` | Get current user profile |
| PATCH | `/api/v1/users/me` | Update username / bio |
| POST | `/api/v1/users/me/avatar` | Upload profile image |

### Memories
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/memories` | Create today's memory |
| GET | `/api/v1/memories/calendar` | Get yearly calendar data |
| GET | `/api/v1/memories/{date}` | Get memory detail by date |

### Stats
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/stats/overview` | Streak, avg rating, record rate |
| GET | `/api/v1/stats/mood` | Most frequent mood |
| GET | `/api/v1/stats/yearly-average` | Monthly average rating |
| GET | `/api/v1/stats/yearly-mood` | Mood distribution |

---

## Local Development

### Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv)

### Setup

```bash
# Clone
git clone https://github.com/your-username/jodjam-backend.git
cd jodjam-backend

# Install dependencies
uv sync

# Copy environment file
cp .env.example .env
# Fill in your values in .env

# Run
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`  
Swagger docs at `http://localhost:8000/docs`

---

## Environment Variables

```env
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
DATABASE_URL=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=
FRONTEND_URL=
JWT_SECRET=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
ENV=development
```

---

## Key Design Decisions

- **One memory per day** — enforced at DB level via `UniqueConstraint("user_id", "memory_date")`
- **Memory is final** — no UPDATE or DELETE endpoints for memories
- **Cookie-based auth** — `httponly` cookies for security, backend manages all token logic
- **Private storage** — Supabase bucket is private, backend generates signed URLs

---

## License

MIT
