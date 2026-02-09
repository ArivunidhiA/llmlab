# LLMLab Frontend

Production-ready React dashboard for AI model cost management and optimization.

## Features

- 📊 **Real-time Analytics** - Monitor spending across all AI models
- 💰 **Cost Tracking** - Detailed breakdown by model and time period
- ⚠️ **Smart Alerts** - Budget threshold notifications
- 💡 **AI Recommendations** - Personalized cost optimization suggestions
- 🔐 **Secure API Keys** - Manage integration credentials safely
- 🌙 **Dark Mode** - Full dark mode support
- 📱 **Responsive** - Mobile-friendly design
- ✅ **Type-Safe** - Full TypeScript support

## Tech Stack

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Testing**: Jest + React Testing Library
- **Form Validation**: Native HTML5 + Custom

## Getting Started

### Prerequisites

- Node.js 18+ or higher
- npm/yarn/pnpm

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API URL
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
npm run build
npm start
```

## Project Structure

```
llmlab/frontend/
├── app/                          # Next.js app directory
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Landing page
│   ├── login/
│   ├── signup/
│   ├── dashboard/
│   └── settings/
├── components/                   # Reusable UI components
│   ├── Button.tsx
│   ├── Card.tsx
│   ├── Alert.tsx
│   ├── Input.tsx
│   ├── Header.tsx
│   ├── CostCard.tsx
│   ├── BarChart.tsx
│   ├── LineChart.tsx
│   └── BudgetProgressBar.tsx
├── lib/                         # Utility functions
│   ├── utils.ts                # General utilities
│   └── api.ts                  # API client
├── types/                       # TypeScript types
│   └── index.ts
├── __tests__/                   # Unit tests
├── globals.css                  # Global styles
├── tailwind.config.ts
├── tsconfig.json
└── next.config.ts
```

## API Integration

The frontend communicates with the backend via the `lib/api.ts` module. Configure your API URL:

```bash
# In .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Available Endpoints

- `POST /auth/signup` - Create account
- `POST /auth/login` - Login
- `GET /dashboard/metrics` - Get dashboard data
- `GET /api-keys` - List API keys
- `POST /api-keys` - Create API key
- `DELETE /api-keys/{id}` - Delete API key
- `GET /budget` - Get budget settings
- `PUT /budget` - Update budget limit
- `GET /alerts` - List budget alerts
- `POST /alerts` - Create alert
- `PUT /alerts/{id}` - Update alert

## Features

### Pages

#### Landing Page
- Hero section with CTA
- Features showcase
- Pricing table
- FAQ section

#### Authentication
- Sign up with email/password
- Login page
- Form validation
- Error handling

#### Dashboard
- Total spend card
- Monthly and daily spend tracking
- Budget progress bar with alerts
- Spend by model bar chart
- Spend trends line chart
- AI-powered recommendations
- Model usage breakdown

#### Settings
- API key management (create, copy, delete)
- Budget limit configuration
- Budget alerts setup
- User profile (extensible)

### Components

**UI Components**
- `Button` - Multiple variants and sizes
- `Card` - With header, body, footer
- `Alert` - Info, success, warning, error
- `Input` - With validation and helpers
- `Header` - Navigation with user menu

**Dashboard Components**
- `CostCard` - Display spending metrics
- `BarChart` - Model cost visualization
- `LineChart` - Spending trends
- `BudgetProgressBar` - Budget status with alerts

## Testing

```bash
# Run tests
npm test

# Watch mode
npm test:watch

# Coverage
npm test -- --coverage
```

## Dark Mode

Dark mode is automatically enabled based on user preference or system settings. Users can toggle it via the header button. The preference is saved in localStorage.

## Performance Optimizations

- Code splitting with dynamic imports
- Image optimization
- CSS-in-JS with Tailwind (no extra CSS)
- Optimized recharts bundle imports
- Debounced API polling

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari 14+, Chrome Mobile)

## Environment Variables

```
NEXT_PUBLIC_API_URL      - Backend API base URL (required)
NEXT_PUBLIC_ENABLE_ANALYTICS - Enable analytics (default: true)
NEXT_PUBLIC_ENABLE_DARK_MODE - Enable dark mode (default: true)
```

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

### Traditional Hosting

```bash
npm run build
# Deploy the .next folder and public folder
npm start
```

## Customization

### Colors

Edit `tailwind.config.ts` to customize colors:

```typescript
colors: {
  blue: '#3b82f6',
  green: '#10b981',
  // ...
}
```

### API Polling

Adjust polling interval in `lib/api.ts`:

```typescript
pollMetrics(callback, 30000) // 30 seconds
```

## Troubleshooting

### Port already in use
```bash
npm run dev -- -p 3001
```

### Build errors
```bash
rm -rf .next node_modules
npm install
npm run build
```

### API connection issues
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Check backend is running
- Review CORS configuration

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please create an issue in the repository.
