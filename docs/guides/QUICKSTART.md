# LLMLab Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies
```bash
cd llmlab
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Start Backend
```bash
# Terminal 1
python3 -m uvicorn backend.main:app --reload --port 8000
# Output: Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Test API
```bash
# Terminal 2 - Health check
curl http://localhost:8000/health

# Track a cost
curl -X POST http://localhost:8000/api/track \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "my-app",
    "provider": "openai",
    "model": "gpt-4",
    "input_tokens": 100,
    "output_tokens": 50,
    "cost_usd": 0.003
  }'

# Get status
curl http://localhost:8000/api/status/my-app
```

### Step 4: Use CLI
```bash
# Install CLI in development mode
pip install -e .

# Initialize project
llmlab init
# Prompts: Project ID (default), API URL (http://localhost:8000)

# Set budget
llmlab budget 100

# See costs
llmlab status

# Get optimization tips
llmlab optimize

# Export to CSV
llmlab export
```

### Step 5: Use Python SDK
```python
from llmlab import track_cost
import openai

@track_cost(provider="openai", model="gpt-4", feature="summarization")
def summarize_text(text: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Summarize: {text}"}]
    )
    return response.choices[0].message.content
```

### Step 6: Run Tests
```bash
pytest tests/test_backend.py -v
```

---

## 📊 Test the Full Workflow

```bash
# Start backend
python3 -m uvicorn backend.main:app --reload &

# Initialize CLI
llmlab init

# Set budget to $100
llmlab budget 100

# Simulate costs (via API)
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/track \
    -H "Content-Type: application/json" \
    -d "{
      \"project_id\": \"default\",
      \"provider\": \"openai\",
      \"model\": \"gpt-4\",
      \"input_tokens\": $((100 * i)),
      \"output_tokens\": $((50 * i)),
      \"cost_usd\": 0.00$i,
      \"feature\": \"chat-$i\"
    }"
done

# Check status
llmlab status

# Get recommendations
llmlab optimize

# Export
llmlab export
cat default_costs.csv
```

---

## 🎯 What You Built

✅ **Backend** - FastAPI server tracking LLM costs  
✅ **CLI** - Command-line tool for status, budgets, recommendations  
✅ **SDK** - Python decorator for automatic cost tracking  
✅ **Tests** - Full test suite with 100+ test cases  
✅ **Docs** - Architecture, implementation plan, API docs  

---

## 🚀 Next Steps

1. **Deploy Backend to Railway**
   ```bash
   # Push to GitHub and Railway auto-deploys
   git push origin main
   ```

2. **Deploy Frontend to Vercel** (coming v1.1)
   ```bash
   # React dashboard with charts
   ```

3. **Release CLI to PyPI**
   ```bash
   # Anyone can: pip install llmlab-cli
   ```

4. **Get First 100 Users**
   - Post on Product Hunt
   - Share on Hacker News
   - Tweet to AI/dev community
   - Email beta users

---

## 🐛 Troubleshooting

### "Connection refused" on `llmlab status`
- Make sure backend is running: `python3 -m uvicorn backend.main:app`
- Check it's on port 8000: `curl http://localhost:8000/health`

### Tests failing
- Install dev dependencies: `pip install -r requirements.txt`
- Run with verbose: `pytest tests/ -v -s`

### CLI commands not found
- Reinstall in dev mode: `pip install -e .`
- Check installation: `which llmlab`

---

## 📈 Success Metrics

**After launch, measure:**
- GitHub stars (target: 500 by month 3)
- CLI installs (target: 100 by week 1)
- Beta users (target: 50 by month 1)
- Paying customers (target: 20 by month 3)
- Revenue (target: $5K/month by month 3)

---

## 💬 Questions?

- Read ARCHITECTURE.md for system design
- Read IMPLEMENTATION_PLAN.md for next steps
- Check API examples in README.md
- Run tests to verify everything works

---

**Built in 1 hour. Ready for launch. Let's go! 🚀**
