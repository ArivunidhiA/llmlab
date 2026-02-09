# LLMLab Frontend - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
```bash
# Check Node.js version (need 18+)
node --version
npm --version
```

### 1. Installation

```bash
cd llmlab/frontend

# Install dependencies
npm install
```

### 2. Configure Environment

```bash
# Create env file
cp .env.example .env.local

# Edit .env.local (optional - defaults to localhost:8000)
# NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### 3. Start Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📋 Common Tasks

### Run Tests

```bash
# Run all tests
npm test

# Watch mode (auto-rerun on changes)
npm test:watch

# With coverage report
npm test -- --coverage
```

### Type Check

```bash
npm run type-check
```

### Build for Production

```bash
npm run build
npm start
```

### Lint Code

```bash
npm run lint
```

## 🎯 Testing the Features

### 1. Landing Page
- Visit [http://localhost:3000](http://localhost:3000)
- See hero, features, pricing, CTA
- Scroll through all sections

### 2. Sign Up
- Click "Get Started Free" or "Sign Up"
- Fill in: name, email, password
- Submit form
- Should redirect to dashboard

### 3. Dashboard
- View cost cards (with mock data)
- See bar chart for model costs
- See line chart for spending trends
- Check budget progress bar
- View recommendations list
- View model usage breakdown

### 4. Settings
- Manage API keys (create, copy, delete)
- Update budget limit
- Enable/disable budget alerts

### 5. Dark Mode
- Click sun/moon icon in header
- Dark mode persists on page reload
- Try all pages in dark mode

## 📁 Project Structure

```
frontend/
├── app/               # Pages (landing, auth, dashboard, settings)
├── components/        # Reusable UI components
├── lib/               # Utilities and API client
├── types/             # TypeScript interfaces
├── __tests__/         # Unit tests
├── globals.css        # Global styles
└── package.json       # Dependencies
```

## 🔌 API Integration

The app expects a backend at `http://localhost:8000/api` with these endpoints:

### Authentication
```
POST   /auth/signup      Create account
POST   /auth/login       Login
```

### Dashboard
```
GET    /dashboard/metrics   Get all metrics
```

### API Keys
```
GET    /api-keys         List all keys
POST   /api-keys         Create new key
DELETE /api-keys/{id}    Delete key
```

### Budget & Alerts
```
GET    /budget                Get budget settings
PUT    /budget                Update budget
GET    /alerts                List alerts
POST   /alerts                Create alert
PUT    /alerts/{id}           Update alert
```

## 🛠️ Customization

### Change API URL

Edit `.env.local`:
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Update Colors

Edit `tailwind.config.ts`:
```typescript
colors: {
  blue: '#YOUR_COLOR',
}
```

### Adjust Polling Interval

Edit `lib/api.ts` (line ~65):
```typescript
pollMetrics(callback, 60000) // 60 seconds
```

## 🐛 Troubleshooting

### Port 3000 already in use
```bash
npm run dev -- -p 3001
```

### Clear cache and reinstall
```bash
rm -rf .next node_modules package-lock.json
npm install
npm run dev
```

### API connection errors
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Ensure backend is running
- Check browser console for CORS errors

### Dark mode not working
- Clear localStorage: `localStorage.clear()`
- Check system preference in OS settings

## 📦 Key Dependencies

```json
{
  "react": "^18.2.0",           // React
  "next": "^14.0.0",            // Next.js framework
  "recharts": "^2.10.0",        // Charts
  "tailwindcss": "^3.3.6"       // Styling
}
```

## 🧪 What's Tested

- ✅ Button component (all variants)
- ✅ Card component (header, body, footer)
- ✅ Utility functions (formatting, calculations)
- ✅ API integration patterns

## 📊 Mock Data

The app includes realistic mock data for:
- 4 AI models (GPT-4, Claude-3, GPT-3.5, Llama-2)
- 7-day spending trends
- 3 cost optimization recommendations
- Budget tracking (current: $1,240.75 of $2,000)

## 🚢 Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
# Follow prompts
```

### Docker

```bash
docker build -t llmlab-frontend .
docker run -p 3000:3000 llmlab-frontend
```

### Traditional Server

```bash
npm run build
npm start
# Runs on http://localhost:3000
```

## 📚 Documentation

- **README.md** - Full documentation
- **PROJECT_SUMMARY.md** - Architecture overview
- **Components/** - Inline component documentation

## 💡 Tips

1. **Use the component library** - Don't duplicate code
2. **Keep types strong** - TypeScript strict mode is on
3. **Test your changes** - Run `npm test` before committing
4. **Follow conventions** - Use the pattern from existing code
5. **Check dark mode** - Test both light and dark modes

## 🎓 Learning Resources

- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript Docs](https://www.typescriptlang.org/docs)
- [Recharts Docs](https://recharts.org)

## 📞 Support

### Running into issues?

1. Check the troubleshooting section above
2. Review the README.md
3. Check browser console for errors
4. Verify backend is running and accessible

### Want to add features?

1. Create a new branch: `git checkout -b feature/name`
2. Make your changes
3. Test: `npm test`
4. Commit: `git commit -m "feat: description"`
5. Push: `git push origin feature/name`

## ✅ Checklist

Before deploying to production:

- [ ] Backend API is configured
- [ ] Environment variables are set
- [ ] All tests pass: `npm test`
- [ ] No TypeScript errors: `npm run type-check`
- [ ] Build succeeds: `npm run build`
- [ ] Dark mode works
- [ ] Mobile responsive looks good
- [ ] All pages load without errors
- [ ] API calls work correctly

## 🎉 Done!

You now have a fully functional LLMLab dashboard running locally!

**Next Step**: Connect it to your backend API by configuring `NEXT_PUBLIC_API_URL`.
