# Digital Doppelgänger

**Automata-Based Human vs Bot Behavioral Intelligence Platform**

A cybersecurity/behavioral-analysis platform that analyzes user interaction sequences in web applications and determines whether observed behavior is more consistent with a human-like or automated/scripted session. The core detection engine is built on **Automata Theory** — using finite state machines, product automata, and formal language recognition.

## Architecture

```
Frontend (Next.js / React / TypeScript / Tailwind CSS)
   ↓
REST API / WebSocket (FastAPI)
   ↓
Event Processor
   ↓
Feature Extractor
   ↓
Automata Engine (4 DFAs × Product Automaton)
   ↓
Behavioral Scorer
   ↓
Detection Engine
   ↓
PostgreSQL
```

### Automata Engine

The system uses four specialized Deterministic Finite Automata combined via a product automaton:

1. **Navigation Automaton** — Tracks page transitions, back/forward navigation, repeated pages
2. **Interaction Automaton** — Tracks clicks, hovers, keyboard, scroll, form interactions
3. **Timing Automaton** — Tracks inter-event delays, rapid actions, timing regularity
4. **Consistency Automaton** — Tracks behavioral entropy, repetition, pattern diversity

**Product State** = Navigation × Interaction × Timing × Consistency

## Project Structure

```
digital_doppelganger/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── api/                 # REST & WebSocket endpoints
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── automata/            # Automata engine (core)
│   │   │   ├── base.py          # DFA base class & alphabet
│   │   │   ├── navigation.py    # Navigation DFA
│   │   │   ├── interaction.py   # Interaction DFA
│   │   │   ├── timing.py        # Timing DFA
│   │   │   ├── consistency.py   # Consistency DFA
│   │   │   └── product_automaton.py  # Product automaton
│   │   ├── detection/           # Scoring & classification
│   │   ├── simulation/          # Bot profiles
│   │   └── database/            # DB session management
│   ├── tests/                   # 30+ automated tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router pages
│   │   ├── components/          # Shared components
│   │   ├── hooks/               # Custom hooks
│   │   └── lib/                 # API client
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── docs/
```

## Installation

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 16+
- Docker & Docker Compose (optional)

### Docker (Recommended)

```bash
docker compose up --build
```

Frontend: http://localhost:3000
Backend: http://localhost:8000
API Docs: http://localhost:8000/docs

### Local Development

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Set up PostgreSQL database
createdb doppelganger

# Configure environment
cp .env.example .env
# Edit .env with your database URL

# Run
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

#### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Async PostgreSQL URL | `postgresql+asyncpg://postgres:postgres@localhost:5432/doppelganger` |
| `SYNC_DATABASE_URL` | Sync PostgreSQL URL | `postgresql://postgres:postgres@localhost:5432/doppelganger` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `DEBUG` | Debug mode | `true` |

#### Frontend (.env.local)

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL | `ws://localhost:8000` |

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Running the Simulator

```bash
# Via API
curl -X POST http://localhost:8000/api/simulator/run \
  -H "Content-Type: application/json" \
  -d '{"profile": "scripted_bot", "event_count": 50}'
```

Or use the web interface at `/simulator`.

## Running Experiments

```bash
curl -X POST http://localhost:8000/api/experiments/run \
  -H "Content-Type: application/json" \
  -d '{"human_count": 100, "bot_count": 100, "adversarial_count": 100}'
```

Or use the web interface at `/analytics`.

## Pages

| Route | Description |
|-------|-------------|
| `/` | Landing page |
| `/dashboard` | Real-time monitoring dashboard |
| `/playground` | DoppelShop — interactive behavioral playground |
| `/simulator` | Bot simulation profiles |
| `/sessions` | Session explorer |
| `/sessions/[id]` | Session details with replay |
| `/compare` | Side-by-side session comparison |
| `/automata` | Automata Theory laboratory |
| `/attack-lab` | Adversarial testing lab |
| `/analytics` | Experiment dashboard |

## API Examples

### Create a session
```bash
curl -X POST http://localhost:8000/api/sessions
```

### Send an event
```bash
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "event_type": "mouse_click",
    "timestamp": 1727651234.567,
    "page": "/products",
    "target": "add_to_cart"
  }'
```

### Get automata definitions
```bash
curl http://localhost:8000/api/automata/definitions
```

## Privacy

This is a behavioral analysis research platform. It does **not** collect passwords, payment information, personal messages, or unnecessary personally identifiable information. All sessions use anonymous UUIDs.

## Disclaimer

This system uses automata-based heuristics to assess behavioral patterns. It does **not** claim to definitively prove that a user is human or a bot. Results are labeled as "Human-like", "Automated-like", "Suspicious", or "Inconclusive" based on observed behavioral signals. Experiment results apply to synthetic test datasets only and do not establish real-world detection accuracy.
