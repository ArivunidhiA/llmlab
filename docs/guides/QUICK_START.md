# LLMLab Backend - Quick Start Guide

**Get running in 5 minutes!**

---

## 1️⃣ Install Dependencies

```bash
cd llmlab/backend
pip install -r requirements.txt --break-system-packages
```

---

## 2️⃣ Setup Environment

```bash
cp .env.example .env
```

Then edit `.env` with:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SECRET_KEY=your-secret-key
```

---

## 3️⃣ Start Server

```bash
python main.py
```

Or use the script:
```bash
./run.sh
```

Server runs at: **http://localhost:8000**

---

## 4️⃣ Try API

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Sign Up
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe"
  }'
```

Save the `access_token` from response.

### Track Event
```bash
curl -X POST http://localhost:8000/api/events/track \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
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
curl http://localhost:8000/api/costs/summary \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

### Get Recommendations
```bash
curl http://localhost:8000/api/recommendations \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

---

## 5️⃣ View Interactive Docs

Open: **http://localhost:8000/docs**

(Try all endpoints interactively!)

---

## 📚 Full Documentation

- **Setup & Usage:** `README.md`
- **API Endpoints:** `API_SPEC.md`
- **Build Details:** `BUILD_SUMMARY.md`
- **Integration:** `BACKEND_MANIFEST.md`

---

## 🧪 Run Tests

```bash
pytest tests/ -v
```

---

## 🆘 Stuck?

**Check:**
1. Python 3.9+ installed: `python --version`
2. Dependencies installed: `pip list | grep fastapi`
3. Port 8000 free: `lsof -i :8000`
4. .env file exists: `ls -la .env`

---

## ✨ What's Included?

✅ 7 API routes (23 endpoints)  
✅ 3 LLM providers (OpenAI, Anthropic, Google)  
✅ Cost calculation engine  
✅ Smart recommendations  
✅ Budget management  
✅ 40+ tests  
✅ Full documentation  

---

**Ready? Start with `python main.py` → http://localhost:8000/docs** 🚀
