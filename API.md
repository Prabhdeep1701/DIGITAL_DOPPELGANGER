# API Reference

Base URL: `http://localhost:8000`

## Health Check

```
GET /api/health
→ { "status": "ok", "service": "digital-doppelganger" }
```

## Sessions

### Create Session
```
POST /api/sessions
Body: { "is_simulated": "optional_profile_name" }
→ { "session_id": "uuid", "user_id": "uuid" }
```

### End Session
```
POST /api/sessions/{session_id}/end
→ { "automation_score": 42.3, "classification": "suspicious", ... }
```

### List Sessions
```
GET /api/sessions?limit=50&classification=automated_like
→ [{ "id", "classification", "score", "event_count", ... }]
```

### Get Session Detail
```
GET /api/sessions/{session_id}
→ { "events": [...], "automaton_states": [...], "detections": [...], "scoring_breakdown": {...} }
```

### Dashboard Stats
```
GET /api/sessions/dashboard
→ { "total_sessions", "human_like", "automated_like", "average_score", ... }
```

### Compare Sessions
```
GET /api/sessions/compare/{session_a_id}/{session_b_id}
→ { "session_a": {...}, "session_b": {...}, "comparison": {...} }
```

## Events

### Send Event
```
POST /api/events
Body: { "session_id", "event_type", "timestamp", "page", "target" }
→ { "product_state": {...}, "transitions": [...], "is_suspicious": false }
```

### Batch Events
```
POST /api/events/batch
Body: { "events": [...] }
→ { "processed": 10, "results": [...] }
```

### Session Events
```
GET /api/events/session/{session_id}
→ [{ "event_type", "timestamp", "page", "target", "sequence_number" }]
```

## Automata

### Get Definitions
```
GET /api/automata/definitions
→ { "alphabet": [...], "automata": [{ "name", "states", "transitions", ... }] }
```

### Process Sequence
```
POST /api/automata/process-sequence
Body: [{ "event_type", "timestamp" }]
→ { "results": [...], "final_state": {...}, "suspicious_counts": {...} }
```

### Generate Sequence
```
POST /api/automata/generate-sequence
Body: { "sequence_type": "valid|suspicious|invalid", "length": 15 }
→ { "sequence": [...], "is_accepted": true }
```

### Find Counterexample
```
POST /api/automata/counterexample
Body: [{ "event_type", "timestamp" }]
→ { "found": true, "violation_index": 5, "expected_symbols": [...], ... }
```

## Simulator

### Run Simulation
```
POST /api/simulator/run
Body: { "profile": "scripted_bot", "event_count": 50 }
→ { "session_id", "classification", "score", "scoring_breakdown" }
```

### List Profiles
```
GET /api/simulator/profiles
→ { "profiles": [{ "name", "description" }] }
```

### Adversarial Test
```
POST /api/simulator/adversarial
Body: { "test_type": "slow", "event_count": 60 }
→ { "classification", "score", "explanation" }
```

## Experiments

### Run Experiment
```
POST /api/experiments/run
Body: { "human_count": 100, "bot_count": 100, "adversarial_count": 100 }
→ { "accuracy", "precision", "recall", "f1_score", "confusion_matrix", ... }
```

## WebSocket

### Event Stream
```
WS /ws/events/{session_id}
Send: { "event_type", "timestamp", "page", "target" }
Receive: { "product_state", "transitions", "is_suspicious", "detections" }
```

### Dashboard Stream
```
WS /ws/dashboard
Receive: { "type": "event", "session_id", "event_type", "is_suspicious" }
```
