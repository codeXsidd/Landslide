# NER-SAGE Coding Standards

## Python (Backend)

### Style
- Line length: 100 characters (ruff enforced)
- Formatter: ruff format
- Linter: ruff check with E, F, I, N, W, UP, B, C4, SIM rules
- Type checker: mypy

### Naming
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions / methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Pydantic models: `PascalCase` with suffix `Model` (e.g. `RiskPredictionModel`)
- Pydantic schemas (API): `PascalCase` with suffix `Request` / `Response` / `Schema`

### Imports
```python
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party
from fastapi import FastAPI
from pydantic import BaseModel

# 3. Internal (absolute)
from app.config.settings import settings
from app.database.mongodb import get_database
```

### Docstrings
Use Google-style docstrings for all public functions and classes:
```python
def calculate_decision_value(
    uncertainty_reduction: float,
    decision_importance: float,
    reliability: float,
    acquisition_cost: float,
) -> float:
    """Calculate the decision value of an evidence acquisition action.

    Args:
        uncertainty_reduction: Expected reduction in entropy (0-1).
        decision_importance: Weight of this decision (0-1).
        reliability: Expected reliability of the new evidence (0-1).
        acquisition_cost: Cost of acquiring the evidence (0-1, higher = more costly).

    Returns:
        Decision value score (higher = more valuable to acquire).

    Raises:
        ValueError: If acquisition_cost is zero.
    """
```

### Async
- All database operations MUST be async (use motor for MongoDB, async neo4j driver).
- FastAPI route handlers MUST be `async def`.
- CPU-bound ML operations should be run in a thread pool via `asyncio.run_in_executor`.

### Error Handling
- Use custom exception classes in `app/exceptions.py`.
- Never swallow exceptions silently.
- Log all exceptions with context before re-raising.

### Pydantic Models
- Use `model_config = ConfigDict(...)` not the deprecated `class Config`.
- Always include field descriptions in `Field(description="...")`.
- Use `datetime` with timezone awareness.

---

## TypeScript (Frontend)

### Style
- Line length: 100 characters
- Formatter: Prettier
- Linter: ESLint with Next.js config

### Naming
- Files: `PascalCase.tsx` for components, `camelCase.ts` for utilities/services
- Components: `PascalCase`
- Hooks: `use` prefix (e.g. `useRiskData`)
- Types / Interfaces: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- API services: `camelCase` functions in `src/services/`

### Component Structure
```typescript
// 1. Imports
import { useState } from 'react'
import type { RiskPrediction } from '@/types/risk'

// 2. Types (local to file)
interface RiskCardProps {
  prediction: RiskPrediction
  showConfidence?: boolean
}

// 3. Component
export function RiskCard({ prediction, showConfidence = true }: RiskCardProps) {
  // hooks at top
  const [expanded, setExpanded] = useState(false)

  // event handlers
  const handleToggle = () => setExpanded(!expanded)

  // render
  return (
    <div>...</div>
  )
}
```

### State Management
- Use **Zustand** for global app state (risk data, simulation, decisions).
- Use **TanStack Query** for server state (API data fetching, caching, invalidation).
- Do NOT use useState for data that should be fetched from the API.

### API Calls
- All API calls go through `src/services/api.ts` base client.
- Never call `fetch` directly in components.
- Always handle loading and error states.

---

## Git

### Commit Messages
```
type(scope): short description

Types: feat, fix, docs, style, refactor, test, chore
Scope: backend, frontend, ml, evidence, graph, rag, scripts
```

Examples:
```
feat(evidence): add contradiction detector for rainfall vs satellite
fix(graph): handle disconnected components in isolation calculation
docs(api): update risk endpoint OpenAPI descriptions
test(evidence): add unit tests for next-best evidence engine
```

### Branch Strategy
- `main`: stable, demo-ready
- `dev`: integration branch
- `feat/<name>`: feature branches
- `fix/<name>`: bug fix branches

---

## Environment
- Never hardcode credentials, API keys, or secrets.
- Always use `settings` from `app/config/settings.py`.
- All configurable values must have a corresponding env variable in `.env.example`.
