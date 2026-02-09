# LLMlab - Architecture Diagrams

## System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A["User App<br/>(OpenAI/Anthropic)"]
        CLI["CLI<br/>(llmlab status)"]
        WEB["Web Dashboard<br/>(Next.js)"]
    end
    
    subgraph "SDK & Tracking"
        SDK["LLMlab SDK<br/>(@track_cost)"]
        QUEUE["Event Queue<br/>(Async)"]
    end
    
    subgraph "Backend"
        API["FastAPI<br/>(main.py)"]
        MODELS["Models<br/>(SQLAlchemy)"]
        AUTH["Auth<br/>(JWT)"]
    end
    
    subgraph "Data Layer"
        DB["Supabase<br/>(PostgreSQL)"]
        CACHE["Redis<br/>(Optional)"]
    end
    
    subgraph "Services"
        CALC["Cost Calc Engine"]
        ALERT["Alert Service<br/>(Slack/Email)"]
        RECOM["Recommendations<br/>Engine"]
    end
    
    A -->|LLM API Call| SDK
    CLI -->|Query| API
    WEB -->|GET /api/*| API
    SDK -->|Async Event| QUEUE
    QUEUE -->|POST /track| API
    API -->|SQL| DB
    API -->|Check| CACHE
    DB -->|Data| CALC
    CALC -->|Generate| ALERT
    DB -->|Analyze| RECOM
    RECOM -->|Update| WEB
    
    style A fill:#e1f5ff
    style SDK fill:#f3e5f5
    style API fill:#fff3e0
    style DB fill:#e8f5e9
```

## Database Schema

```mermaid
erDiagram
    USERS ||--o{ EVENTS : tracks
    USERS ||--o{ BUDGETS : sets
    USERS ||--o{ API_KEYS : has
    EVENTS ||--o{ COSTS : calculates
    
    USERS {
        uuid id
        string email
        string password_hash
        timestamp created_at
        string slack_webhook
        string discord_webhook
    }
    
    API_KEYS {
        uuid id
        uuid user_id
        string provider
        string encrypted_key
        timestamp created_at
    }
    
    EVENTS {
        uuid id
        uuid user_id
        string provider
        string model
        integer input_tokens
        integer output_tokens
        float duration_ms
        timestamp created_at
    }
    
    COSTS {
        uuid id
        uuid event_id
        float amount_usd
        string currency
        timestamp calculated_at
    }
    
    BUDGETS {
        uuid id
        uuid user_id
        float monthly_limit
        string alert_channel
        float alert_at_50_percent
        float alert_at_80_percent
        timestamp created_at
    }
```

## User Flow

```mermaid
sequenceDiagram
    actor User
    participant CLI as CLI Tool
    participant SDK as LLMlab SDK
    participant API as Backend<br/>(FastAPI)
    participant DB as Database
    participant Dashboard as Dashboard
    
    User->>CLI: llmlab init <api-key>
    CLI->>API: POST /auth/signup
    API->>DB: Create user + API key
    API-->>CLI: ✅ Setup complete
    
    User->>SDK: @track_cost decorator
    SDK->>API: POST /api/events/track<br/>(async)
    API->>DB: Insert event + cost
    DB-->>Dashboard: Update real-time
    
    User->>Dashboard: View dashboard
    Dashboard->>API: GET /api/costs/summary
    API->>DB: Aggregate costs
    API-->>Dashboard: Return summary
    
    Dashboard-->>User: Show spend cards<br/>& charts
    
    Note over User,DB: Budget Alert Flow
    
    API->>DB: Check budget threshold
    DB-->>API: Current: $4000/$5000
    API->>API: Trigger 80% alert
    API->>API: Send Slack webhook
    
    Note over Dashboard,User: Alert delivered
```

## Event Tracking Flow

```mermaid
graph LR
    A["User Code:<br/>@track_cost decorator"] -->|Wrap LLM Call| B["Decorator Captures:<br/>- Model<br/>- Tokens<br/>- Duration<br/>- Cost"]
    B -->|Async Send| C["Event Queue<br/>(Non-blocking)"]
    C -->|HTTP POST| D["Backend API<br/>/api/events/track"]
    D -->|Validate| E["Schema Check<br/>(Pydantic)"]
    E -->|Calculate Cost| F["Cost Engine<br/>(Provider rates)"]
    F -->|Store| G["Database<br/>(PostgreSQL)"]
    G -->|Trigger| H["Alerts<br/>(Slack/Email/Webhook)"]
    H -->|Update| I["Dashboard<br/>(Real-time)"]
    
    style A fill:#e1f5ff
    style C fill:#fff3e0
    style D fill:#ffe0b2
    style G fill:#e8f5e9
    style I fill:#f3e5f5
```

## Provider Integration Pattern

```mermaid
graph TB
    subgraph "User Layer"
        A["User Code"]
    end
    
    subgraph "Provider Adapters"
        B1["OpenAI<br/>Adapter"]
        B2["Anthropic<br/>Adapter"]
        B3["Google<br/>Adapter"]
        B4["Cohere<br/>Adapter"]
    end
    
    subgraph "Unified Interface"
        C["Provider Base Class<br/>(protocols.py)"]
    end
    
    subgraph "Core Tracking"
        D["Event Normalizer"]
        E["Cost Calculator"]
    end
    
    A -->|API Call| B1
    A -->|API Call| B2
    A -->|API Call| B3
    A -->|API Call| B4
    
    B1 -->|Extends| C
    B2 -->|Extends| C
    B3 -->|Extends| C
    B4 -->|Extends| C
    
    C -->|Normalize| D
    D -->|Calculate| E
    E -->|Track| F["Database"]
    
    style C fill:#fff3e0
    style D fill:#f3e5f5
    style E fill:#e8f5e9
```

## Cost Calculation Logic

```mermaid
graph LR
    A["Event Received<br/>(provider, model,<br/>input_tokens,<br/>output_tokens)"] -->|Lookup| B["Provider Pricing<br/>(config.json)"]
    B -->|Get Rates| C["Input Rate<br/>$0.03/1K<br/>Output Rate<br/>$0.06/1K"]
    C -->|Calculate| D["input_cost =<br/>tokens * rate / 1000"]
    D -->|+| E["output_cost =<br/>tokens * rate / 1000"]
    E -->|=| F["Total Cost<br/>rounded to<br/>4 decimals"]
    F -->|Store| G["Database"]
    G -->|Aggregate| H["Dashboard<br/>(daily/weekly/monthly)"]
    
    style A fill:#e1f5ff
    style B fill:#fff3e0
    style C fill:#ffe0b2
    style F fill:#f3e5f5
    style H fill:#e8f5e9
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Vercel (Frontend)"
        FE["Next.js App<br/>- pages/<br/>- components/<br/>- styles/"]
        FE_ENV["Environment<br/>- API_URL<br/>- AUTH_TOKEN"]
    end
    
    subgraph "Railway (Backend)"
        BE["FastAPI<br/>- main.py<br/>- models.py<br/>- database.py"]
        BE_ENV["Environment<br/>- DATABASE_URL<br/>- JWT_SECRET<br/>- PROVIDER_RATES"]
    end
    
    subgraph "Supabase (Database)"
        DB["PostgreSQL<br/>- Users<br/>- Events<br/>- Costs<br/>- Budgets"]
        AUTH["Auth<br/>- JWT tokens<br/>- API keys"]
    end
    
    FE -->|API calls| BE
    BE -->|SQL| DB
    BE -->|Verify| AUTH
    FE -->|Verify| AUTH
    
    style FE fill:#bbdefb
    style BE fill:#ffe0b2
    style DB fill:#c8e6c9
```

---

**Key Design Principles:**
1. **Async-first** — Event tracking never blocks user code
2. **Extensible** — Easy to add new LLM providers
3. **Stateless backend** — Scale horizontally
4. **Real-time dashboard** — WebSocket or polling updates
5. **Privacy-first** — Users own their data, open-source auditable code
