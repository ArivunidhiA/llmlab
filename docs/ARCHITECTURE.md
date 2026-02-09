# LLMLab System Architecture

Complete system design documentation with diagrams.

---

## System Architecture Diagram

```mermaid
graph TB
    subgraph Client["Client Layer"]
        Browser["🌐 React Browser App<br/>(Vercel)"]
        CLI["💻 Python CLI<br/>(PyPI Package)"]
        SDK["🐍 Python SDK<br/>(pip install)"]
    end
    
    subgraph API["API Gateway"]
        FastAPI["⚡ FastAPI Backend<br/>(Railway)"]
    end
    
    subgraph DB["Data Layer"]
        Postgres["🗄️ PostgreSQL<br/>(Supabase)"]
    end
    
    subgraph External["External Services"]
        Auth["🔐 Supabase Auth"]
        Email["📧 Email (Future)"]
    end
    
    Browser -->|HTTPS REST| FastAPI
    CLI -->|HTTPS REST| FastAPI
    SDK -->|HTTP POST| FastAPI
    
    FastAPI -->|SQL Queries| Postgres
    FastAPI -->|Auth Check| Auth
    FastAPI -->|Send Alerts| Email
    
    style Browser fill:#61affe
    style CLI fill:#61affe
    style SDK fill:#61affe
    style FastAPI fill:#90ee90
    style Postgres fill:#ffa500
    style Auth fill:#dda0dd
```

---

## User Flow Diagram

```mermaid
graph LR
    A["User"] -->|1. Sign Up| B["Create Account"]
    B -->|2. Get API Key| C["Receive llmlab_xxx"]
    C -->|3a. CLI: llmlab init| D["CLI Setup"]
    C -->|3b. Python: sdk.init()| E["SDK Setup"]
    C -->|3c. Web App| F["Login to Dashboard"]
    
    D -->|4. llmlab status| G["View Spend"]
    E -->|4. Track Costs| G
    F -->|4. Real-time Updates| G
    
    G -->|5. llmlab optimize| H["Get Recommendations"]
    F -->|5. View Recommendations| H
    
    style A fill:#e1f5ff
    style B fill:#fff9c4
    style C fill:#fff9c4
    style D fill:#c8e6c9
    style E fill:#c8e6c9
    style F fill:#c8e6c9
    style G fill:#ffe0b2
    style H fill:#f8bbd0
```

---

## Cost Tracking Flow

```mermaid
graph TB
    subgraph "Application Code"
        A["LLM API Call<br/>OpenAI/Claude/Gemini"]
    end
    
    subgraph "Instrumentation"
        B["SDK Decorator<br/>@track_cost"]
        C["Extract Tokens<br/>from Response"]
    end
    
    subgraph "Processing"
        D["Calculate Cost<br/>Based on Pricing"]
        E["Validate Budget<br/>Alert if 80%+"]
    end
    
    subgraph "Storage"
        F["Save to Database<br/>cost_events table"]
    end
    
    subgraph "Visualization"
        G["Dashboard<br/>Show Trends"]
        H["CLI<br/>show spend"]
        I["Recommendations<br/>Cost Optimization"]
    end
    
    A -->|Tokens + Response| B
    B -->|Extract| C
    C -->|Calculate| D
    D -->|Check| E
    E -->|Store| F
    F -->|Query| G
    F -->|Query| H
    F -->|Analyze| I
    
    style A fill:#ffcccc
    style B fill:#ffffcc
    style C fill:#ffffcc
    style D fill:#ccffcc
    style E fill:#ccffcc
    style F fill:#ccccff
    style G fill:#ffe6cc
    style H fill:#ffe6cc
    style I fill:#ffe6cc
```

---

## Database Schema

```mermaid
erDiagram
    USERS ||--o{ COST_EVENTS : logs
    USERS ||--o{ BUDGETS : has
    
    USERS {
        bigint id PK
        string email UK
        string hashed_password
        string api_key UK
        timestamp created_at
        float monthly_budget
        float budget_alert_threshold
    }
    
    COST_EVENTS {
        bigint id PK
        bigint user_id FK
        string provider
        string model
        integer input_tokens
        integer output_tokens
        float cost
        timestamp timestamp
        string metadata
    }
    
    BUDGETS {
        bigint id PK
        bigint user_id FK
        string month
        float budget_amount
        boolean alert_sent
    }
```

---

## API Endpoint Hierarchy

```mermaid
graph TD
    ROOT["/"]
    HEALTH["GET /health"]
    
    API["API /api"]
    
    AUTH["AUTH /api/auth"]
    AUTH_SIGNUP["POST /signup"]
    AUTH_LOGIN["POST /login"]
    AUTH_LOGOUT["POST /logout"]
    
    EVENTS["EVENTS /api/events"]
    EVENTS_TRACK["POST /track"]
    
    COSTS["COSTS /api/costs"]
    COSTS_SUMMARY["GET /summary"]
    
    BUDGETS["BUDGETS /api/budgets"]
    BUDGETS_GET["GET /budgets"]
    BUDGETS_SET["POST /budgets"]
    
    RECS["RECS /api/recommendations"]
    RECS_GET["GET /recommendations"]
    
    ROOT --> HEALTH
    ROOT --> API
    
    API --> AUTH
    API --> EVENTS
    API --> COSTS
    API --> BUDGETS
    API --> RECS
    
    AUTH --> AUTH_SIGNUP
    AUTH --> AUTH_LOGIN
    AUTH --> AUTH_LOGOUT
    
    EVENTS --> EVENTS_TRACK
    
    COSTS --> COSTS_SUMMARY
    
    BUDGETS --> BUDGETS_GET
    BUDGETS --> BUDGETS_SET
    
    RECS --> RECS_GET
    
    style ROOT fill:#e8f5e9
    style HEALTH fill:#c8e6c9
    style API fill:#fff9c4
    style AUTH fill:#ffe0b2
    style EVENTS fill:#ffccbc
    style COSTS fill:#ffb3ba
    style BUDGETS fill:#ffb3ba
    style RECS fill:#ff99ac
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph Local["Developer Machine"]
        Code["GitHub Repo<br/>Push Code"]
    end
    
    subgraph CDN["CDN / Edge"]
        Vercel["📊 Vercel<br/>Frontend Distribution"]
    end
    
    subgraph Compute["Compute"]
        Railway["⚡ Railway<br/>FastAPI Backend"]
    end
    
    subgraph Data["Data"]
        Supabase["🗄️ Supabase<br/>PostgreSQL"]
    end
    
    subgraph Package["Package Registry"]
        PyPI["📦 PyPI<br/>Python Package"]
    end
    
    Code -->|git push| Vercel
    Code -->|git push| Railway
    Code -->|npm publish<br/>twine upload| PyPI
    
    Railway -->|SQL| Supabase
    Vercel -->|HTTPS| Railway
    
    User["👤 User"] -->|Web| Vercel
    User -->|CLI: pip install| PyPI
    User -->|CLI| Railway
    
    style Code fill:#e3f2fd
    style Vercel fill:#f3e5f5
    style Railway fill:#e8f5e9
    style Supabase fill:#fff3e0
    style PyPI fill:#fce4ec
    style User fill:#c8e6c9
```

---

## Request/Response Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI as CLI/SDK
    participant Backend as FastAPI
    participant DB as PostgreSQL
    
    User->>CLI: llmlab status
    CLI->>Backend: GET /api/costs/summary
    Backend->>DB: SELECT * FROM cost_events WHERE user_id=X
    DB-->>Backend: [cost_events]
    Backend->>Backend: Aggregate & Calculate
    Backend-->>CLI: {total_spend, by_model, trends}
    CLI->>CLI: Format Output
    CLI-->>User: Pretty Table
    
    User->>CLI: llmlab optimize
    CLI->>Backend: GET /api/recommendations
    Backend->>DB: SELECT * FROM cost_events (last 30 days)
    DB-->>Backend: [events]
    Backend->>Backend: Analyze Patterns
    Backend-->>CLI: [recommendations]
    CLI->>CLI: Format Output
    CLI-->>User: Recommendation List
```

---

## Cost Calculation Engine

```mermaid
graph LR
    Input["Input<br/>provider: 'openai'<br/>model: 'gpt-4'<br/>input_tokens: 1000<br/>output_tokens: 500"]
    
    Lookup["Lookup Pricing<br/>OpenAI GPT-4<br/>in=0.03/1k<br/>out=0.06/1k"]
    
    Calculate["Calculate<br/>in: (1000/1000)*0.03<br/>out: (500/1000)*0.06<br/>total = 0.03 + 0.03"]
    
    Output["Output<br/>cost: 0.06"]
    
    Store["Store<br/>INSERT cost_events<br/>cost=0.06"]
    
    Input --> Lookup
    Lookup --> Calculate
    Calculate --> Output
    Output --> Store
    
    style Input fill:#c8e6c9
    style Lookup fill:#ffccbc
    style Calculate fill:#ffe0b2
    style Output fill:#ffb3ba
    style Store fill:#f8bbd0
```

---

## Recommendation Engine Logic

```mermaid
graph TD
    A["Analyze User Cost Events<br/>(Last 30 days)"]
    
    B["Count Model Usage<br/>GPT-4: 50 calls<br/>Claude: 10 calls"]
    
    C{High Usage<br/>of Expensive<br/>Model?}
    
    D["Check Token Count<br/>Avg: 2500 tokens<br/>Industry: 1200"]
    
    E{Over Average?}
    
    F["Check Provider Mix<br/>OpenAI only?<br/>No Anthropic?"]
    
    G{Single<br/>Provider?}
    
    H["Generate<br/>Recommendation 1<br/>Switch to GPT-4 Turbo<br/>Save: 70%"]
    
    I["Generate<br/>Recommendation 2<br/>Optimize Prompts<br/>Save: 25%"]
    
    J["Generate<br/>Recommendation 3<br/>Try Claude<br/>Save: 40%"]
    
    K["Rank by<br/>Confidence &<br/>Savings"]
    
    L["Return Top<br/>Recommendations"]
    
    A --> B
    B --> C
    C -->|Yes| H
    C -->|No| D
    D --> E
    E -->|Yes| I
    E -->|No| F
    F --> G
    G -->|Yes| J
    G -->|No| K
    
    H --> K
    I --> K
    J --> K
    K --> L
    
    style A fill:#c8e6c9
    style H fill:#ffe0b2
    style I fill:#ffe0b2
    style J fill:#ffe0b2
    style K fill:#ffb3ba
    style L fill:#f8bbd0
```

---

## Provider Extensibility Pattern

```mermaid
graph LR
    A["Abstract Provider<br/>Interface"]
    
    B["OpenAI<br/>Adapter"]
    C["Anthropic<br/>Adapter"]
    D["Google<br/>Adapter"]
    E["Custom<br/>Adapter"]
    
    F["Provider Factory<br/>get_provider<br/>name"]
    
    G["Cost Calculator<br/>Uses Factory<br/>to get Provider"]
    
    A -->|implements| B
    A -->|implements| C
    A -->|implements| D
    A -->|implements| E
    
    F -->|routes to| B
    F -->|routes to| C
    F -->|routes to| D
    F -->|routes to| E
    
    G -->|uses| F
    
    style A fill:#e1f5ff
    style B fill:#c8e6c9
    style C fill:#c8e6c9
    style D fill:#c8e6c9
    style E fill:#fff9c4
    style F fill:#ffe0b2
    style G fill:#f8bbd0
```

---

## CLI Command Flow

```mermaid
graph TB
    A["User Input<br/>llmlab optimize"]
    
    B["Parse Command<br/>Click Framework"]
    
    C["Load Config<br/>~/.llmlab/config.json"]
    
    D["Initialize SDK<br/>LLMLab api_key"]
    
    E["Call API<br/>GET /api/recommendations"]
    
    F["Format Output<br/>Tabulate + Colors"]
    
    G["Display Results<br/>Terminal"]
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    
    style A fill:#e3f2fd
    style B fill:#bbdefb
    style C fill:#90caf9
    style D fill:#64b5f6
    style E fill:#42a5f5
    style F fill:#2196f3
    style G fill:#1976d2
```

---

## Security & Auth Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Web App
    participant Backend as FastAPI
    participant DB as PostgreSQL
    
    User->>Frontend: Enter email + password
    Frontend->>Backend: POST /api/auth/signup
    Backend->>Backend: Hash password with bcrypt
    Backend->>DB: INSERT user
    DB-->>Backend: user_id
    Backend->>Backend: Create JWT token
    Backend-->>Frontend: {token, api_key}
    Frontend->>Frontend: Store token in session
    
    User->>Frontend: Make API call
    Frontend->>Backend: GET /api/costs (Authorization: Bearer token)
    Backend->>Backend: Verify JWT signature
    Backend->>Backend: Extract user_id from token
    Backend->>DB: SELECT costs WHERE user_id=X
    DB-->>Backend: costs
    Backend-->>Frontend: {costs}
```

---

**Diagrams above can be rendered as SVG/PNG using:**
- Mermaid Live Editor: https://mermaid.live
- GitHub Markdown (native support)
- Convert to image: `mmdc -i ARCHITECTURE.md -o ARCHITECTURE.pdf`

