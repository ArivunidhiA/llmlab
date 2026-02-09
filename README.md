# LLMLab

Track and optimize your LLM API costs in seconds.

## What is LLMLab?

LLMLab gives you **visibility** into how much you're spending on OpenAI, Anthropic, Google Gemini, and other LLM APIs.

**The problem**: Most developers have no idea how much they're spending on LLMs. You call an API, it works, but you never check the costs.

**The solution**: LLMLab watches your API calls, calculates costs, and shows you:
- How much you spent today/this month
- Which models cost the most
- Simple optimization tips

No code changes needed. Just swap your API key.

## Get Started (2 minutes)

### Option 1: CLI (Recommended)

```bash
pip install llmlab-cli
llmlab login
llmlab stats
```

### Option 2: Web Dashboard

Open your browser and log in with GitHub. See costs in real-time.

### Option 3: Python SDK

```python
from llmlab import track_cost

@track_cost(provider="openai")
def my_function():
    # your LLM code here
    pass
```

## Features

- **Real-time tracking** — See costs as they happen
- **Multi-provider** — OpenAI, Anthropic, Google Gemini
- **Zero code changes** — Works with existing code
- **Beautiful dashboard** — See cost breakdowns by model
- **CLI tool** — Quick commands for stats
- **Open source** — No hidden fees, forever free

## Architecture

```
Your Code
   ↓
LLMLab Proxy / SDK
   ↓
LLM API (OpenAI, Anthropic, etc.)
   ↓
Logged to Dashboard
```

## Tech Stack

- **Backend**: FastAPI + Python
- **Frontend**: Next.js + React
- **Database**: PostgreSQL
- **Deployment**: Railway (backend), Vercel (frontend)

## Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# CLI
cd cli
pip install -e .
llmlab --help
```

## Testing

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test

# CLI tests
cd cli && pytest
```

## Contributing

We welcome contributions! Check the issues or start with adding a new LLM provider.

## License

MIT

## Questions?

- Open an issue on GitHub
- Check the docs/ folder for more details

---

**Built with simplicity in mind. Track your costs. Save money. Move on.**
