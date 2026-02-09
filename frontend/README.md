# LLMLab Frontend

A beautiful, minimal dashboard for tracking LLM costs. Built with Next.js 14, React, TypeScript, and Tailwind CSS.

## Features

- 🎯 **Landing Page** - Clean hero, problem/solution, install instructions
- 📊 **Dashboard** - Real-time cost tracking with charts and tables
- 🌙 **Dark Mode** - Auto-detects system preference, manual toggle
- 📱 **Responsive** - Works on mobile, tablet, and desktop
- 🔐 **GitHub OAuth** - Secure authentication
- ⚡ **Real-time Updates** - Polls backend every 5 seconds

## Quick Start

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Edit .env.local with your values
# - NEXT_PUBLIC_API_URL
# - NEXT_PUBLIC_GITHUB_CLIENT_ID
# - NEXT_PUBLIC_GITHUB_REDIRECT_URI

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Landing page
│   ├── dashboard/
│   │   └── page.tsx          # Dashboard page
│   ├── auth/
│   │   └── callback/
│   │       └── page.tsx      # OAuth callback
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── components/
│   ├── Navigation.tsx        # Header with user menu
│   ├── Button.tsx            # Reusable button
│   ├── CostCard.tsx          # Cost metric card
│   ├── ModelChart.tsx        # Bar chart by model
│   └── DailyTable.tsx        # Daily costs table
├── lib/
│   ├── api.ts                # API client with auth
│   └── utils.ts              # Helper functions
├── types/
│   └── index.ts              # TypeScript interfaces
└── __tests__/                # Jest tests
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_GITHUB_CLIENT_ID` | GitHub OAuth App ID | `abc123` |
| `NEXT_PUBLIC_GITHUB_REDIRECT_URI` | OAuth callback URL | `http://localhost:3000/auth/callback` |

## Scripts

```bash
npm run dev       # Start development server
npm run build     # Build for production
npm run start     # Start production server
npm run lint      # Run ESLint
npm run test      # Run tests
npm run test:watch # Run tests in watch mode
```

## API Integration

The frontend expects these backend endpoints:

```
POST /auth/github/callback  - Exchange OAuth code for JWT
GET  /api/v1/stats          - Get cost statistics
GET  /api/v1/keys           - Get user's API keys
POST /api/v1/keys           - Create new API key
DELETE /api/v1/keys/:id     - Delete API key
GET  /api/v1/me             - Get current user
```

## Styling

- **Tailwind CSS** - Utility-first CSS framework
- **No component library** - All components hand-crafted
- **Apple-inspired** - Minimal, clean, lots of whitespace
- **System fonts** - Uses native font stack for performance

## Testing

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import to Vercel
3. Add environment variables
4. Deploy

### Docker

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

## Tech Stack

- **Next.js 14** - React framework with App Router
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Recharts** - Charts
- **Jest** - Testing

## License

MIT
