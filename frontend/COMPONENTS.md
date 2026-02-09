# LLMLab Frontend - Component Library Reference

Complete documentation of all reusable UI components.

## 📚 Table of Contents

1. [Basic Components](#basic-components)
2. [Layout Components](#layout-components)
3. [Dashboard Components](#dashboard-components)
4. [Examples](#examples)

---

## Basic Components

### Button

Reusable button component with multiple variants and sizes.

**Location**: `components/Button.tsx`

**Props**:
```typescript
interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  children: ReactNode;
}
```

**Variants**:
- `primary` - Blue button (main action)
- `secondary` - Light gray button
- `outline` - Border only button
- `ghost` - Transparent with hover effect
- `danger` - Red button for destructive actions

**Sizes**:
- `sm` - Small button (padding: px-3 py-1.5)
- `md` - Medium button (padding: px-4 py-2) - Default
- `lg` - Large button (padding: px-6 py-3)

**Examples**:
```tsx
// Primary button
<Button onClick={handleClick}>Click me</Button>

// Secondary button
<Button variant="secondary">Cancel</Button>

// Loading state
<Button isLoading={isLoading}>Save</Button>

// Danger button
<Button variant="danger">Delete</Button>

// Large outline button
<Button variant="outline" size="lg">Learn More</Button>
```

---

### Input

Text input component with validation support.

**Location**: `components/Input.tsx`

**Props**:
```typescript
interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helper?: string;
  icon?: React.ReactNode;
}
```

**Features**:
- Label display
- Error message
- Helper text below input
- Optional icon (left side)
- Password type support
- All HTML input types supported

**Examples**:
```tsx
// Basic input
<Input
  label="Email"
  type="email"
  placeholder="you@example.com"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
/>

// With error
<Input
  label="Password"
  type="password"
  error="Password must be at least 8 characters"
/>

// With helper text and icon
<Input
  label="Amount"
  type="number"
  helper="Enter amount in USD"
  icon={<DollarIcon />}
/>
```

---

### Alert

Alert/notification component for messages.

**Location**: `components/Alert.tsx`

**Props**:
```typescript
interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "info" | "success" | "warning" | "error";
  title?: string;
  children: ReactNode;
  onClose?: () => void;
}
```

**Variants**:
- `info` - Blue background, information icon
- `success` - Green background, checkmark icon
- `warning` - Yellow background, warning icon
- `error` - Red background, error icon

**Features**:
- Title support
- Optional close button
- Color-coded icons
- Dark mode support

**Examples**:
```tsx
// Simple alert
<Alert variant="info">
  This is an informational message
</Alert>

// With title
<Alert variant="success" title="Success!">
  Your changes have been saved
</Alert>

// Dismissible alert
<Alert 
  variant="warning" 
  title="Warning"
  onClose={() => setShowAlert(false)}
>
  This action cannot be undone
</Alert>
```

---

## Layout Components

### Header

Navigation header with dark mode toggle and user menu.

**Location**: `components/Header.tsx`

**Props**:
```typescript
interface HeaderProps {
  user?: User;
  showNav?: boolean;
}
```

**Features**:
- Logo with home link
- Navigation menu (conditional)
- Dark mode toggle button
- User profile menu with logout
- Sticky positioning
- Responsive design

**Examples**:
```tsx
// Without user (landing page)
<Header showNav={true} />

// With user (authenticated pages)
<Header 
  showNav={true} 
  user={{ name: "John Doe", email: "john@example.com" }}
/>
```

---

### Card

Container component with header, body, and footer sections.

**Location**: `components/Card.tsx`

**Components**:
- `Card` - Main container
- `CardHeader` - Header section with title/subtitle
- `CardBody` - Main content area
- `CardFooter` - Bottom section (usually for actions)

**Card Props**:
```typescript
interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "elevated";
  children: ReactNode;
}
```

**Variants**:
- `default` - Border with light shadow
- `elevated` - Border with stronger shadow, hover effect

**Examples**:
```tsx
// Basic card
<Card>
  <CardBody>Simple card content</CardBody>
</Card>

// Full-featured card
<Card variant="elevated">
  <CardHeader title="Settings" subtitle="Manage your account" />
  <CardBody>
    <p>Settings content here</p>
  </CardBody>
  <CardFooter>
    <Button>Save</Button>
    <Button variant="secondary">Cancel</Button>
  </CardFooter>
</Card>
```

---

## Dashboard Components

### CostCard

Displays a cost metric with trend indicator.

**Location**: `components/CostCard.tsx`

**Props**:
```typescript
interface CostCardProps {
  title: string;
  amount: number;
  change?: number;
  trend?: "up" | "down" | "neutral";
}
```

**Features**:
- Large currency display
- Trend indicator (↑ ↓ →)
- Color-coded text (red/green/gray)
- Percentage change

**Examples**:
```tsx
<CostCard
  title="Total Spend"
  amount={4250.50}
  change={15.3}
  trend="up"
/>

<CostCard
  title="Daily Cost"
  amount={42.15}
  change={-2.5}
  trend="down"
/>
```

---

### BarChart

Bar chart visualization for categorical data.

**Location**: `components/BarChart.tsx`

**Props**:
```typescript
interface BarChartProps {
  data: BarChartData[];
  dataKey: string;
  xAxis?: string;
  title?: string;
  height?: number;
}
```

**Data Format**:
```typescript
interface BarChartData {
  name: string;
  [key: string]: any;
}
```

**Examples**:
```tsx
const data = [
  { name: "GPT-4", cost: 520.5 },
  { name: "Claude-3", cost: 380.25 },
  { name: "GPT-3.5", cost: 240.0 },
];

<BarChart
  data={data}
  dataKey="cost"
  title="Spend by Model"
  height={300}
/>
```

---

### LineChart

Line chart visualization for time-series data.

**Location**: `components/LineChart.tsx`

**Props**:
```typescript
interface LineChartProps {
  data: LineChartData[];
  dataKey: string;
  title?: string;
  height?: number;
}
```

**Data Format**:
```typescript
interface LineChartData {
  date: string;
  [key: string]: any;
}
```

**Examples**:
```tsx
const trendData = [
  { date: "Jan 1", amount: 35 },
  { date: "Jan 5", amount: 45 },
  { date: "Jan 10", amount: 38 },
];

<LineChart
  data={trendData}
  dataKey="amount"
  title="Spending Trends"
  height={350}
/>
```

---

### BudgetProgressBar

Budget status visualization with alerts.

**Location**: `components/BudgetProgressBar.tsx`

**Props**:
```typescript
interface BudgetProgressBarProps {
  spent: number;
  limit: number;
  showAlert?: boolean;
}
```

**Features**:
- Percentage calculation
- Color-coded progress bar (green/yellow/red)
- Remaining amount display
- Auto alert when nearing/exceeding budget
- Responsive design

**Colors**:
- Green: 0-50%
- Yellow: 51-80%
- Red: 81-100%+

**Examples**:
```tsx
<BudgetProgressBar
  spent={1240.75}
  limit={2000}
  showAlert={true}
/>
```

---

## Examples

### Complete Dashboard Card

```tsx
<Card variant="elevated">
  <CardHeader 
    title="API Keys" 
    subtitle="Manage your integration keys"
  />
  <CardBody className="space-y-4">
    {apiKeys.map((key) => (
      <div key={key.id} className="p-4 bg-slate-50 rounded-lg">
        <p className="font-semibold">{key.name}</p>
        <p className="text-sm text-slate-500">{key.key}</p>
      </div>
    ))}
  </CardBody>
  <CardFooter>
    <Button>Add Key</Button>
  </CardFooter>
</Card>
```

### Authentication Form

```tsx
<Card>
  <CardBody className="space-y-6">
    <h1 className="text-2xl font-bold">Login</h1>
    
    <Input
      label="Email"
      type="email"
      placeholder="you@example.com"
      value={email}
      onChange={(e) => setEmail(e.target.value)}
      error={emailError}
    />
    
    <Input
      label="Password"
      type="password"
      value={password}
      onChange={(e) => setPassword(e.target.value)}
      error={passwordError}
    />
    
    <Button 
      isLoading={isLoading}
      onClick={handleLogin}
      className="w-full"
    >
      Sign In
    </Button>
  </CardBody>
</Card>
```

### Dashboard Overview

```tsx
<>
  <Header user={user} />
  
  {/* Cost Cards Grid */}
  <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <CostCard
      title="Total Spend"
      amount={metrics.total_spend}
      change={15.3}
      trend="up"
    />
    <CostCard
      title="This Month"
      amount={metrics.monthly_spend}
      change={8.2}
      trend="up"
    />
  </div>

  {/* Charts Grid */}
  <div className="grid lg:grid-cols-2 gap-8">
    <Card variant="elevated">
      <CardHeader title="Spend by Model" />
      <CardBody>
        <BarChart
          data={metrics.spend_by_model}
          dataKey="cost"
        />
      </CardBody>
    </Card>

    <Card variant="elevated">
      <CardBody>
        <BudgetProgressBar
          spent={metrics.monthly_spend}
          limit={metrics.budget_limit}
        />
      </CardBody>
    </Card>
  </div>

  {/* Trends */}
  <Card variant="elevated">
    <CardHeader title="Spending Trends" />
    <CardBody>
      <LineChart
        data={metrics.spend_trends}
        dataKey="amount"
      />
    </CardBody>
  </Card>
</>
```

---

## Styling

All components use Tailwind CSS with:
- **Light mode**: White backgrounds, dark text
- **Dark mode**: Slate-900 backgrounds, light text
- **Consistent spacing**: Using Tailwind's spacing scale
- **Responsive design**: Mobile-first approach
- **Smooth transitions**: All interactive elements

### Color Palette

```
Primary: Blue-600 (#3b82f6)
Success: Green-600 (#16a34a)
Warning: Yellow-600 (#ca8a04)
Error: Red-600 (#dc2626)
Background: White / Slate-950
Text: Slate-900 / Slate-50
```

---

## Best Practices

1. **Always use Card** for content containers
2. **Use proper Button variants** for different actions
3. **Show validation errors** with Input component
4. **Alert users** before destructive actions
5. **Keep charts responsive** with proper height
6. **Test dark mode** on all pages
7. **Use TypeScript** for all props
8. **Follow spacing** with Tailwind's gap/space
9. **Maintain accessibility** with proper labels
10. **Test on mobile** for responsive design

---

## Troubleshooting

### Charts not rendering
- Check data format (must have required fields)
- Ensure height prop is set
- Check for console errors

### Dark mode not working
- Verify globals.css is imported
- Check localStorage for theme setting
- Ensure html element has dark class

### Button not responding
- Check onClick handler is defined
- Verify isLoading state isn't true
- Check disabled prop

### Input validation not showing
- Ensure error prop is passed
- Verify form validation logic
- Check error state is updating

---

## Component Status

| Component | Status | Tests | Docs |
|-----------|--------|-------|------|
| Button | ✅ | ✅ | ✅ |
| Input | ✅ | ⚠️ | ✅ |
| Alert | ✅ | ⚠️ | ✅ |
| Header | ✅ | ⚠️ | ✅ |
| Card | ✅ | ✅ | ✅ |
| CostCard | ✅ | ⚠️ | ✅ |
| BarChart | ✅ | ⚠️ | ✅ |
| LineChart | ✅ | ⚠️ | ✅ |
| BudgetProgressBar | ✅ | ⚠️ | ✅ |

✅ = Complete | ⚠️ = Can be expanded | ❌ = Not started

---

**Last Updated**: February 9, 2024
**Version**: 1.0.0
