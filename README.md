# 🏔️ NER-SAGE

## Northeast Region — Self-Adaptive Geospatial Emergency Intelligence

> **"When the AI is uncertain, it knows what to ask next."**

**Smart India Hackathon 2026 — Problem Statement 2**  
**Domain:** AI + Geospatial Intelligence + Disaster Management  
**Target Region:** Northeast India  
**Architecture:** Software-only · Polyglot Database · Self-Questioning AI

---

## 🚀 What Is NER-SAGE?

NER-SAGE is not a landslide prediction dashboard.

It is a **Landslide Decision Intelligence System** — an AI platform that:

1. **Predicts** landslide risk with calibrated probability
2. **Questions** its own prediction by measuring uncertainty
3. **Identifies** what evidence is missing, stale, or conflicting
4. **Selects** the next most valuable observation to reduce decision uncertainty
5. **Verifies** citizen and field evidence using computer vision
6. **Updates** its belief after verification
7. **Simulates** road blockage, village isolation, and hospital accessibility loss
8. **Recommends** the action with greatest expected harm reduction
9. **Awaits** authorized human approval before any critical action
10. **Learns** from outcomes to improve future decisions

### The Core Question

> **"If I am uncertain, what should I check next — and why does that check matter?"**

---

## 🏗️ Architecture

```
USER
  │
  ▼
React / Next.js UI  (GIS + Decision Interface)
  │
  ▼
FastAPI Backend
  │
  ├─── MongoDB         Evidence, Risk, Locations, Documents
  ├─── Neo4j           Road Graph, Village Isolation, Connectivity
  ├─── Redis           Cache, Temporary State, Job Queues
  └─── Qdrant          RAG Vector Store (Groq Embeddings)
  │
  ▼
Evidence Fusion Engine
  │
  ▼
ML Risk Engine (XGBoost + Random Forest + Calibration)
  │
  ▼
Uncertainty Engine → Self-Questioning Engine
  │
  ▼
Next-Best-Evidence Engine
  │
  ▼
Human Verification → Belief Update
  │
  ▼
Consequence Engine (Road Blockage → Isolation → Hospital Access)
  │
  ▼
Simulation + Optimization Engine
  │
  ▼
Decision Engine → Human Review → Action → Outcome → Calibration
```

---

## 🗄️ Database Stack

| Technology | Role |
|------------|------|
| **MongoDB** | Primary operational store — evidence, risk, documents |
| **Neo4j** | Road connectivity graph — isolation, routing, cascades |
| **Redis** | Cache, temporary simulation state, rate limiting |
| **Qdrant** | RAG vector search (Groq embeddings) |
| **MinIO** | Object storage — images, DEMs, satellite files |

> ⚠️ PostgreSQL is **not used** in this project by design.

---

## ⚡ Quick Start

### Prerequisites

- Docker Desktop (running)
- Python 3.11+
- Node.js 20+
- Git

### 1. Clone & Configure

```bash
git clone <repo-url> ner-sage
cd ner-sage
cp .env.example .env
# Edit .env — add GROQ_API_KEY and NEO4J_PASSWORD
```

### 2. Start Infrastructure

```bash
docker compose up -d
docker compose ps        # all services should show "healthy"
```

### 3. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r ../requirements.txt
uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### 5. Seed Demo Data

```bash
python scripts/generate_synthetic_data.py
python scripts/seed_neo4j.py
```

### 6. Run SIH Demo Scenario

```bash
python scripts/run_demo.py
```

---

## 🎭 SIH Demo Scenario — Road B Incident

The demo replays the complete NER-SAGE decision loop:

| Step | Action |
|------|--------|
| 1 | Risk = 82%, Confidence = 54% |
| 2 | Satellite STALE · Ground Evidence MISSING · Sources CONFLICTING |
| 3 | AI: "Verify Road B — Decision Value = VERY HIGH" |
| 4 | Human submits: partial debris, fresh cracks, water seepage |
| 5 | Risk → 88%, Confidence → 91% |
| 6 | Road B blocked → Village X isolated → Hospital access degraded |
| 7 | Simulation: Rainfall +25% |
| 8 | Risk → 94%, Isolation → 84% |
| 9 | Recommend: Inspect Road B, Prepare Route C, Pre-position Team |
| 10 | Human APPROVES |
| 11 | Outcome recorded → Calibration updated |

---

## 📁 Project Structure

```
ner-sage/
├── backend/          FastAPI application + all engines
├── frontend/         Next.js 15 + React 19 + Leaflet GIS
├── scripts/          Data generation, seeding, demo runner
├── ml/               Training pipelines + model artifacts
├── data/             Raw + processed + synthetic datasets
├── tests/            Unit, integration, API, E2E tests
├── docs/             Architecture + API + engine docs
├── docker/           Dockerfiles + nginx config
├── .agents/          Project rules + agent workflows
└── docker-compose.yml
```

---

## 🧠 Signature Innovation: Self-Questioning Decision Loop

```
Traditional:   PREDICT → ALERT

NER-SAGE:      PREDICT → DOUBT → INVESTIGATE → VERIFY
               → UPDATE → ASSESS CONSEQUENCES → SIMULATE
               → PRIORITIZE → HUMAN APPROVAL → ACT → LEARN
```

The Next-Best-Evidence Engine scores candidate observations by:

```
Decision Value = (Uncertainty Reduction × Decision Importance × Reliability)
                 ÷ Acquisition Cost
```

This answers not just "what reduces model uncertainty?" but:

> **"What evidence produces the greatest decision value given who could be harmed?"**

---

## 🌐 Data Sources

- **Terrain:** SRTM DEM, slope, aspect, drainage
- **Rainfall:** IMD observations + forecasts
- **Satellite:** Sentinel-1, Sentinel-2, NISAR (where available)
- **Roads/Villages:** OpenStreetMap NER + government GIS
- **Landslide Inventory:** NDMA, BSDMA, state databases
- **Documents:** Government SOPs, emergency procedures (for RAG)

> In demo mode, all data is synthetic and clearly labelled `is_simulated: true`.

---

## 🛡️ Safety Principles

1. AI output is **decision support**, not an official emergency warning
2. Critical actions always require **authorized human approval**
3. All simulated data is **explicitly labelled**
4. Missing evidence does **not automatically reduce risk**
5. Conflicting evidence is **surfaced, not silently averaged**
6. Every recommendation includes a **why** explanation

---

## 🧪 Testing

```bash
make test          # run full test suite
pytest tests/      # backend only
cd frontend && npm test  # frontend only
```

---

## 🏆 Hackathon Context

**Smart India Hackathon 2026 · Problem Statement 2**  
Prototype developed for research and demonstration purposes.  
Not an official emergency warning authority.  
© 2026 NER-SAGE Project Team.
