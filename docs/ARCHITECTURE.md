# LLMLab Technical Architecture

## System Overview

```
┌─────────────────┐         ┌─────────────────┐         ┌──────────────────┐
│   Web Dashboard │         │   Python CLI    │         │  Python SDK      │
│  (React/Next)   │         │  (pip install)  │         │  (@decorator)    │
│   (Vercel)      │         │  (PyPI)         │         │  (PyPI)          │
└────────┬────────┘         └────────┬────────┘         └────────┬─────────┘
         │                           │                           │
         │                           │                           │
         └───────────────┬───────────┴───────────────┬───────────┘
                         │                           │
                    HTTPS API                   REST API Calls
                         │                           │
         ┌───────────────▼───────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│      FastAPI Backend (Railway)             │
│  ┌──────────────────────────────────────┐  │
│  │ Routes:                              │  │
│  │  - POST /api/events/track            │  │
│  │  - GET /api/costs/summary            │  │
│  │  - GET /api/budgets                  │  │
│  │  - POST /api/budgets                 │  │
│  │  - GET /api/recommendations          │  │
│  │  - POST /api/auth/signup             │  │
│  │  - POST /api/auth/login              │  │
│  │  - GET /health                       │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │ Business Logic:                      │  │
│  │  - Cost Engine (calculations)        │  │
│  │  - Recommendations Engine            │  │
│  │  - Provider Abstraction              │  │
│  │  - Auth + Security                   │  │
│  └──────────────────────────────────────┘  │
└────────┬──────────────────────────────────┘
         │
         │ SQL/psycopg2
         │
         ▼
┌──────────────────────────────┐
│   Supabase PostgreSQL        │
│  (Database + Auth)           │
│  ┌──────────────────────────┐│
│  │ Tables:                  ││
│  │  - users                 ││
│  │  - projects              ││
│  │  - cost_events           ││
│  │  - budgets               ││
│  └──────────────────────────┘│
└──────────────────────────────┘
```

---

## Architecture Layers

### 1. **Presentation Layer** (Frontend)

**Technology**: React 18 + Next.js 14 + TypeScript + Tailwind CSS

**Deployed**: Vercel (auto-deploys from GitHub)

**Responsibilities**:
- Real-time dashboard display
- Budget alert UI
- Recommendation cards
- User settings
- Beautiful, responsive design

**Key Components**:
- `Header` - Navigation + user menu
- `CostCard` - Display total spend
- `BarChart` - Model breakdown
- `LineChart` - Spend trends
- `BudgetProgressBar` - Budget status
- `RecommendationCard` - Cost-saving tips

**Performance**:
- Server-side rendering (SSR) for fast initial load
- Client-side caching for dashboard data
- Real-time polling of backend API (5-second intervals)

---

### 2. **API Layer** (Backend)

**Technology**: FastAPI + Python 3.9+ + Pydantic + SQLAlchemy

**Deployed**: Railway (auto-deploys from GitHub, with custom domain)

**Responsibilities**:
- REST API endpoints
- Request/response validation
- Authentication + JWT tokens
- Business logic orchestration
- Database operations

**Key Endpoints**:

```
POST /api/events/track          → Log LLM call
GET /api/costs/summary          → Get spend dashboard
GET /api/budgets                → Get budget status
POST /api/budgets               → Set/update budget
GET /api/recommendations        → Get cost-saving tips
POST /api/auth/signup           → Create account
POST /api/auth/login            → Login
GET /health                     → Uptime check
```

**Request/Response Format**: JSON

**Authentication**: JWT tokens (issued on login, validated on protected endpoints)

**Rate Limiting**: 100 requests/minute per API key (to prevent abuse)

---

### 3. **Business Logic Layer**

**Cost Engine**:
- Calculates token costs for each LLM provider
- Aggregates costs by model, provider, date range
- Enforces budget limits
- Generates spend summaries

**Provider Abstraction**:
- Base `Provider` class with abstract methods
- Implementations for OpenAI, Anthropic, Google
- Easy to add new providers (extend base class)
- Real pricing data (updates with API changes)

**Recommendations Engine**:
- Analyzes spending patterns
- Identifies most expensive models
- Suggests cheaper alternatives
- Calculates potential savings

**Example**:
```
User spent:
  - $500 on GPT-4 (100 calls)
  - $50 on GPT-3.5-turbo (1000 calls)

Recommendation:
  "Switch 80% of GPT-4 calls to GPT-3.5-turbo"
  "Save: $400/month"
```

---

### 4. **Data Layer** (Database)

**Technology**: PostgreSQL (via Supabase)

**Deployed**: Supabase cloud (managed)

**Key Tables**:

```sql
-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  api_key VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Cost Events
CREATE TABLE cost_events (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  model VARCHAR(100),
  provider VARCHAR(50),
  tokens_used INT,
  cost_usd DECIMAL(10,6),
  timestamp TIMESTAMP,
  metadata JSONB
);

-- Budgets
CREATE TABLE budgets (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  amount_usd DECIMAL(10,2),
  period VARCHAR(20),  -- 'monthly'
  start_date DATE,
  created_at TIMESTAMP
);

-- Projects (for organizing costs)
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  name VARCHAR(255),
  created_at TIMESTAMP
);
```

**Indexes**:
- `cost_events(user_id, timestamp)` - Fast queries for user spend
- `cost_events(user_id, model)` - Fast model breakdown
- `budgets(user_id)` - Fast budget lookup

---

### 5. **Distribution Layer**

**CLI Tool**:
- Python Click framework
- Installed via PyPI: `pip install llmlab-cli`
- Communicates with backend API
- Stores config in `~/.llmlab/`

**Python SDK**:
- Installed via PyPI: `pip install llmlab-sdk`
- `@track_cost` decorator for auto-tracking
- Integrates into existing Python code with no changes
- Sends costs to backend asynchronously

---

## Technology Stack Justification

| Component | Choice | Why |
|-----------|--------|-----|
| Backend | FastAPI | Fast, async, auto-docs (OpenAPI), production-ready |
| Frontend | React/Next.js | Fast, SSR, great ecosystem, easy deployment to Vercel |
| Database | PostgreSQL | Reliable, scalable, ACID compliance, great for financial data |
| Hosting (Backend) | Railway | Simple, auto-scaling, integrates with GitHub, pay-per-use |
| Hosting (Frontend) | Vercel | Built for Next.js, one-click deploy, CDN, serverless |
| Auth | JWT | Stateless, scalable, API-friendly |
| CLI | Python Click | User-friendly, minimal dependencies |
| SDK | Python | Matches backend language, decorator support, PyPI |

---

## Deployment Architecture

### Development Environment

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m pytest          # Run tests
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# CLI
cd cli
pip install -e .          # Editable install
llmlab init
```

### Production Deployment

**Backend (Railway)**:
1. Connect GitHub repo to Railway
2. Set environment variables (DATABASE_URL, JWT_SECRET, API_KEYS)
3. Deploy button clicks
4. Railway auto-deploys on every git push

**Frontend (Vercel)**:
1. Connect GitHub repo to Vercel
2. Set NEXT_PUBLIC_API_URL environment variable
3. Vercel auto-deploys on every git push
4. Built-in analytics and monitoring

**Database (Supabase)**:
1. Create project via Supabase dashboard
2. Run SQL migrations
3. Get DATABASE_URL
4. Add to Railway environment variables

**CLI (PyPI)**:
1. Build: `python setup.py sdist bdist_wheel`
2. Upload: `twine upload dist/*`
3. Install: `pip install llmlab-cli`

---

## Scalability Considerations

### Current Architecture Handles:
- ✅ 10,000+ daily API calls
- ✅ 1,000+ concurrent users
- ✅ 1M+ cost events in database
- ✅ Real-time dashboard updates

### Future Scaling (v2.0+):
- Caching layer (Redis) for frequently-accessed data
- Read replicas for analytics queries
- GraphQL API (alongside REST)
- WebSocket connections for real-time updates
- Microservices for recommendations engine

---

## Security Considerations

### Authentication
- JWT tokens with 24-hour expiry
- Refresh tokens for long sessions
- Password hashing with bcrypt

### Data Protection
- All API keys stored encrypted in Supabase
- HTTPS enforced
- CORS configured for frontend domain only
- Rate limiting on all endpoints
- Input validation with Pydantic

### Monitoring
- Health checks every 5 minutes (prevent Railway sleep)
- Error logging to stdout (Railway captures)
- Database backups automated (Supabase)

---

## API Response Format

All endpoints return JSON:

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "timestamp": "2024-02-09T10:00:00Z"
}
```

Error responses:

```json
{
  "success": false,
  "data": null,
  "error": "Invalid API key",
  "timestamp": "2024-02-09T10:00:00Z"
}
```

---

## Integration Points

### Frontend ↔ Backend
- REST API (JSON over HTTPS)
- Polling every 5 seconds for fresh data
- WebSocket ready (future enhancement)

### SDK ↔ Backend
- REST API (same endpoints as frontend)
- Async HTTP calls
- Automatic retry on failure

### CLI ↔ Backend
- REST API (JSON over HTTPS)
- Config stored locally in `~/.llmlab/`
- Secure API key handling

---

## Extensibility

### Adding New LLM Provider

1. Create `providers/new_provider.py`
2. Extend `BaseProvider` class
3. Implement `get_cost(tokens, model)` method
4. Add provider to `SUPPORTED_PROVIDERS` dict
5. That's it! No other changes needed

```python
class NewProvider(BaseProvider):
    name = "new_provider"
    models = ["model-a", "model-b"]
    pricing = {
        "model-a": {"input": 0.001, "output": 0.002},
        "model-b": {"input": 0.002, "output": 0.004},
    }
    
    def get_cost(self, tokens_input, tokens_output, model):
        return (tokens_input * self.pricing[model]["input"] +
                tokens_output * self.pricing[model]["output"])
```

---

This architecture is designed for **rapid development**, **easy deployment**, and **effortless scaling**.
