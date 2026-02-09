# LLMLab 🚀

**Free LLM Cost Tracking & Optimization**

Track your OpenAI, Anthropic, and Google Gemini spending in real-time. Get automatic optimization recommendations to cut costs 20-60%.

---

## Features

✅ **Real-time Cost Dashboard**
- Total spend, daily trends, spend by model
- Budget alerts and hard limits
- Beautiful, responsive interface

✅ **Cost Optimization Tips**
- "Switch to Claude 3.5 Sonnet for summarization (save 60%)"
- Automatic model recommendations with confidence scores
- Token optimization suggestions

✅ **Python CLI** (Easy Setup)
```bash
pip install llmlab-cli
llmlab init
llmlab status
llmlab optimize
```

✅ **Python SDK** (Easy Integration)
```python
from llmlab import sdk
sdk.init("your-api-key")
sdk.track_call("openai", "gpt-4", 1000, 500)
```

✅ **Extensible Provider System**
- OpenAI (GPT-4, GPT-3.5, etc.)
- Anthropic (Claude 3 family)
- Google Gemini
- Easy to add more providers

---

## Quick Start

### 1. Sign Up (Free)
```bash
# Visit https://llmlab.vercel.app
# Create account, get API key
```

### 2. Install CLI
```bash
pip install llmlab-cli
llmlab init  # Paste your API key
llmlab status  # See your current spending
```

### 3. Integrate SDK (Optional)
```python
from llmlab import sdk

# Initialize once
sdk.init("your-api-key")

# Track costs manually
sdk.track_call(
    provider="openai",
    model="gpt-4",
    input_tokens=1000,
    output_tokens=500
)

# Get recommendations
recommendations = sdk.get_recommendations()
for rec in recommendations:
    print(f"💡 {rec['title']}: Save {rec['savings_percentage']}%")
```

---

## Architecture

```
LLMLab
├── Backend (FastAPI)
│   ├── Cost tracking API
│   ├── Budget management
│   ├── Recommendation engine
│   └── Deployed on Railway
├── Frontend (React)
│   ├── Dashboard
│   ├── Budget settings
│   ├── Cost trends
│   └── Deployed on Vercel
├── CLI (Python Click)
│   ├── llmlab init
│   ├── llmlab status
│   ├── llmlab optimize
│   └── Installable via PyPI
└── SDK (Python)
    ├── Decorators
    ├── Context managers
    ├── Provider abstraction
    └── Mock-friendly for testing
```

---

## Database Schema

```sql
Users:
- id (PK)
- email (unique)
- hashed_password
- api_key (unique)
- monthly_budget
- budget_alert_threshold (%)

CostEvents:
- id (PK)
- user_id (FK)
- provider (openai, anthropic, google)
- model (gpt-4, claude-3, etc.)
- input_tokens
- output_tokens
- cost ($)
- timestamp

Budgets:
- id (PK)
- user_id (FK)
- month (2026-02)
- budget_amount
- alert_sent
```

---

## API Endpoints

### Authentication
- `POST /api/auth/signup` — Create account
- `POST /api/auth/login` — Login
- `POST /api/auth/logout` — Logout

### Cost Tracking
- `POST /api/events/track` — Track an LLM call
- `GET /api/costs/summary` — Get cost dashboard
- `GET /api/costs/summary?days=7` — Last 7 days

### Budget Management
- `GET /api/budgets` — Get current budget
- `POST /api/budgets` — Set monthly budget

### Recommendations
- `GET /api/recommendations` — Get cost tips

### Health
- `GET /health` — Health check
- `GET /` — API info

---

## CLI Commands

```bash
# Initialize (one-time setup)
llmlab init
# → Asks for API key, saves to ~/.llmlab/config.json

# Check current spending
llmlab status
# → Shows total, by model, by provider, budget status

# Get optimization tips
llmlab optimize
# → Shows "Save 60% by switching to Claude" etc.

# Set monthly budget
llmlab budget --amount 1000
# → Alerts when you hit 80%, blocks at 100%

# Export costs as CSV
llmlab export
# → Creates costs.csv

# Show configuration
llmlab config
# → Displays API key, API URL
```

---

## Supported Models & Pricing

### OpenAI
- gpt-4: $0.03 / 1K input, $0.06 / 1K output
- gpt-4-turbo: $0.01 / 1K input, $0.03 / 1K output
- gpt-3.5-turbo: $0.0005 / 1K input, $0.0015 / 1K output

### Anthropic
- claude-3-opus: $0.015 / 1K input, $0.075 / 1K output
- claude-3-sonnet: $0.003 / 1K input, $0.015 / 1K output
- claude-3-haiku: $0.00025 / 1K input, $0.00125 / 1K output

### Google
- gemini-pro: $0.00025 / 1K input, $0.0005 / 1K output
- gemini-flash: $0.00003 / 1K input, $0.00006 / 1K output

---

## Development

### Setup Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
# Runs on http://localhost:8000
```

### Setup Frontend
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

### Run Tests
```bash
cd tests
pytest test_backend.py -v
```

---

## Roadmap

### ✅ Phase 1 (Week 1)
- [x] Cost dashboard
- [x] Budget alerts
- [x] Basic recommendations
- [x] Python CLI
- [x] Python SDK

### 🚀 Phase 2 (Week 2-4)
- [ ] Per-feature cost attribution
- [ ] A/B testing cost impact
- [ ] Team/project isolation
- [ ] Anomaly detection
- [ ] More provider integrations
- [ ] JavaScript SDK

### 🔥 Future
- Slack integration
- Cost forecasting
- API rate limit recommendations
- Custom pricing import
- Enterprise features

---

## Pricing

**LLMLab is free forever.**

Core features (dashboard, CLI, recommendations) are always free. We believe cost visibility should be universal.

Future premium: Team management, advanced analytics, enterprise integrations (coming later).

---

## FAQ

**Q: Does LLMLab call OpenAI/Anthropic for me?**
A: No, we never call their APIs. You send us the tokens you used, we calculate the cost.

**Q: Where's my data stored?**
A: Supabase PostgreSQL (encrypted). You own your data.

**Q: Can I self-host?**
A: Yes! Open source. Deploy to your infrastructure.

**Q: Does the CLI work offline?**
A: Mostly—you need internet to send costs to the dashboard, but we'll add local tracking.

**Q: How accurate are the recommendations?**
A: We show confidence scores. 85%+ = safe to try. Below 70% = test first.

---

## Contributing

We're open source! PRs welcome for:
- New provider integrations
- Better recommendations
- CLI improvements
- Bug fixes
- Documentation

---

## Support

- 📧 Email: hello@llmlab.dev
- 🐙 GitHub Issues: Report bugs
- 💬 Discord: Community support (coming soon)

---

## License

MIT License - Use freely, modify, commercialize. See LICENSE.

---

**Built by founders, for founders. Let's cut LLM costs together. 🚀**
