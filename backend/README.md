# LLMLab Backend

Production-ready FastAPI backend for cost tracking and optimization across multiple LLM providers.

## Features

✅ **Cost Tracking**: Track API calls from OpenAI, Anthropic, Google Gemini  
✅ **Budget Management**: Set and monitor budget limits  
✅ **Cost Analytics**: Detailed breakdowns by model, provider, and date  
✅ **Smart Recommendations**: AI-powered cost optimization suggestions  
✅ **Anomaly Detection**: Identify unusual spending patterns  
✅ **Provider Abstraction**: Easy to add new LLM providers  
✅ **User Authentication**: JWT-based auth with secure password hashing  
✅ **Production Ready**: Comprehensive tests, error handling, logging  

## Project Structure

```
llmlab/backend/
├── main.py                 # FastAPI app entry point
├── config.py              # Configuration management
├── database.py            # Supabase client
├── models.py              # Pydantic models
├── middleware.py          # Auth & request logging middleware
├── providers/             # Provider abstraction layer
│   ├── base.py           # Abstract provider interface
│   ├── openai.py         # OpenAI provider
│   ├── anthropic.py      # Anthropic provider
│   └── google.py         # Google Gemini provider
├── engines/              # Cost calculation & recommendations
│   ├── cost_engine.py    # Cost calculation engine
│   └── recommendations_engine.py  # Recommendations engine
├── routes/               # API endpoints
│   ├── auth.py          # Authentication routes
│   ├── events.py        # Event tracking routes
│   ├── costs.py         # Cost reporting routes
│   ├── budgets.py       # Budget management routes
│   ├── recommendations.py  # Recommendations routes
│   └── health.py        # Health check routes
├── tests/               # Test suite
│   ├── test_providers.py
│   ├── test_cost_engine.py
│   └── test_api.py
├── requirements.txt     # Python dependencies
└── .env.example        # Environment variables template
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Event Tracking
- `POST /api/events/track` - Track LLM API call
- `GET /api/events/` - List user's events

### Cost Analytics
- `GET /api/costs/summary` - Get cost summary
- `GET /api/costs/by-provider` - Costs by provider
- `GET /api/costs/top-models` - Top models by cost

### Budget Management
- `GET /api/budgets` - List user's budgets
- `POST /api/budgets` - Create/update budget
- `DELETE /api/budgets/{budget_id}` - Delete budget

### Recommendations
- `GET /api/recommendations` - Get all recommendations
- `GET /api/recommendations/anomalies` - Detect anomalies
- `GET /api/recommendations/model-switching` - Model switch recommendations

### Health
- `GET /api/health` - Health check

## Setup & Installation

### Prerequisites
- Python 3.9+
- pip or poetry

### Installation

1. **Clone and navigate to backend directory**
```bash
cd llmlab/backend
```

2. **Install dependencies**
```bash
pip install -r requirements.txt --break-system-packages
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run development server**
```bash
python main.py
```

Server will start at `http://localhost:8000`

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_cost_engine.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## API Usage Examples

### Sign Up
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password",
    "name": "John Doe"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Track Event
```bash
curl -X POST http://localhost:8000/api/events/track \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "model": "gpt-4",
    "input_tokens": 1000,
    "output_tokens": 500
  }'
```

### Get Cost Summary
```bash
curl http://localhost:8000/api/costs/summary?days=30 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "total_cost": 45.67,
  "call_count": 125,
  "average_cost_per_call": 0.3654,
  "by_model": [
    {
      "model": "gpt-4",
      "provider": "openai",
      "total_calls": 50,
      "total_tokens": 50000,
      "total_cost": 30.50
    }
  ],
  "by_date": [...]
}
```

### Set Budget
```bash
curl -X POST http://localhost:8000/api/budgets \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 100.0,
    "period": "monthly"
  }'
```

### Get Recommendations
```bash
curl http://localhost:8000/api/recommendations \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Provider Integration

### Adding a New Provider

1. **Create provider file** (`providers/newprovider.py`):
```python
from .base import BaseProvider
from typing import Tuple

class NewProvider(BaseProvider):
    def __init__(self):
        super().__init__("newprovider")
        self.pricing = {
            "model-1": {"input": 0.001, "output": 0.002},
        }
    
    def get_model_pricing(self, model: str) -> Tuple[float, float]:
        if model in self.pricing:
            pricing = self.pricing[model]
            return pricing["input"], pricing["output"]
        return 0.001, 0.002  # Default
    
    def validate_model(self, model: str) -> bool:
        return True  # Add validation logic
```

2. **Update cost engine** (`engines/cost_engine.py`):
```python
from providers import NewProvider

self.providers["newprovider"] = NewProvider()
```

3. **Use in tracking**:
```bash
curl -X POST http://localhost:8000/api/events/track \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "newprovider",
    "model": "model-1",
    "input_tokens": 100,
    "output_tokens": 50
  }'
```

## Database Schema

### Expected Supabase Tables

```sql
-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  name VARCHAR NOT NULL,
  password_hash VARCHAR NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Events
CREATE TABLE events (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  provider VARCHAR NOT NULL,
  model VARCHAR NOT NULL,
  input_tokens INTEGER,
  output_tokens INTEGER,
  cost DECIMAL,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Budgets
CREATE TABLE budgets (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  limit DECIMAL NOT NULL,
  period VARCHAR NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t llmlab-backend .
docker run -p 8000:8000 --env-file .env llmlab-backend
```

### Railway

1. Connect GitHub repo
2. Add environment variables
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Testing

The backend includes comprehensive test coverage:

- **Unit Tests**: Provider pricing, cost calculations
- **Integration Tests**: API endpoints, auth flows
- **Mock Tests**: Database interactions, error scenarios

Run tests with coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

## Performance Considerations

- **Caching**: Events stored in-memory (mock). Use Redis in production.
- **Database Queries**: Optimize with proper indexing on user_id, timestamp
- **Token Limits**: Implement rate limiting per user
- **Batch Processing**: Consider batch event ingestion for high volume

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message"
}
```

Common status codes:
- `200` - Success
- `201` - Created
- `400` - Bad request
- `401` - Unauthorized
- `404` - Not found
- `500` - Server error

## Security Notes

- ⚠️ Change `SECRET_KEY` in production
- ⚠️ Use HTTPS in production
- ⚠️ Implement rate limiting
- ⚠️ Add CORS restrictions
- ⚠️ Use environment variables for secrets

## Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Make changes and test
3. Commit: `git commit -m "feat: description"`
4. Push: `git push origin feature/name`

## License

MIT

## Support

For issues or questions, contact the development team.
