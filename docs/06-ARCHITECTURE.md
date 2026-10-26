# Architecture

## High-Level Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                         CLI (Rich)                            │
│  menu · Live Alerts · Leads · Account 360 · Money Trail ·    │
│  Network · Complaints · Districts · PDF Export                │
└──────────────────────────┬───────────────────────────────────┘
                           │  direct Python calls
┌──────────────────────────▼───────────────────────────────────┐
│                    CORE (frontend-agnostic)                   │
│                                                               │
│  ┌────────────┐  ┌────────────┐  ┌─────────────┐  ┌────────┐ │
│  │  rules.py  │  │baseline.py │  │    ml.py    │  │fusion. │ │
│  │ 12 RBI     │  │ 90d rolling│  │ RandomForest│  │py      │ │
│  │ flags      │  │ z-scores   │  │ features    │  │weights │ │
│  └─────┬──────┘  └─────┬──────┘  └──────┬──────┘  └───┬────┘ │
│        └────────────────┴────────────────┴─────────────┘      │
│                          │                                    │
│  ┌───────────────────────┼────────────────────────────────┐   │
│  ▼                       ▼                                ▼   │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐   │
│  │ graph_ops.py │  │ complaints.py │  │   report.py      │   │
│  │ networkx     │  │ regex + fuzzy │  │   BSA §63        │   │
│  │ 5-hop BFS    │  │ entity resolve│  │   SHA-256        │   │
│  │ Louvain      │  │ clustering    │  │                  │   │
│  └──────┬───────┘  └───────┬───────┘  └──────────────────┘   │
│         │                  │                                  │
│         └──────────────────┘                                  │
└──────────────────────────┬───────────────────────────────────┘
                           │ loads on start
┌──────────────────────────▼───────────────────────────────────┐
│                        DATA LAYER                             │
│  CSVs in ./data/  (accounts, transactions, complaints)        │
│  + data_gen/generator.py (fixed seed=42 ring + random mode)   │
└──────────────────────────────────────────────────────────────┘
```

## Why This Shape

| Decision | Rationale |
|---|---|
| **Core is frontend-agnostic** | Future web frontend just imports `core/` |
| **No FastAPI** | CLI calls core directly; saves ~3h |
| **No Neo4j** | networkx in-memory graph; persistent via CSV rebuild |
| **No WebSocket** | Rich `Live` replays a pre-generated event queue |
| **No SHAP** | Rule trace + baseline numbers + neighbour risk serve as explanations |
| **No time-decay** | Event-driven score log with append-only history |
| **Terminal first** | Fast to build, runs anywhere, demo-friendly |

## Module Breakdown

| Module | Responsibility | LOC est. |
|---|---|---|
| `core/rules.py` | 12 RBI red-flag rules; returns fired + evidence | 120 |
| `core/baseline.py` | 90-day rolling baseline; z-score deviation | 150 |
| `core/ml.py` | RandomForest training + inference; feature extraction | 200 |
| `core/complaints.py` | Regex + fuzzy entity resolution; incident clustering | 220 |
| `core/graph_ops.py` | 5-hop BFS + chain classifier + Louvain | 200 |
| `core/fusion.py` | Weighted score + event log | 100 |
| `core/report.py` | PDF generation + SHA-256 chain | 180 |
| `data_gen/generator.py` | Fixed ring + background + complaints | 250 |
| `cli/app.py` | Main menu + REPL + 8 screens (`CLIApp.screen_*`) | 820 |
| **Total** | | **~2240 LOC** |

## Data Flow

```
1. STARTUP
   data_gen/generator.py → CSVs → loader → in-memory DataFrames + networkx graph

2. ON DEMAND (any screen)
   account_id → fusion.score()
             → {rule, baseline, ml, complaint, graph}
             → weighted sum → score + tier + contributions

3. ON MONEY TRAIL
   origin_acct → graph_ops.trace() (BFS 5 hops, 24h window)
             → chain classifier → {paths, chain_type, cash_out_points}

4. ON COMPLAINT SEARCH
   query string → complaints.resolve() → {matches, confidence}
              → complaints.linked_to(account) → incident clusters

5. ON PDF EXPORT
   account + all evidence → report.generate_pdf() → SHA-256 → path
```

## Deployment

**Local (hackathon demo):**

```bash
python -m cli.menu --data-dir data/fixed/
```

**Production-ready extensions (documented for judges):**

- Wrap core in FastAPI for web frontend
- Swap CSV loader for Postgres/Neo4j driver
- Add RBAC + audit logger
- Add Kafka consumer for live txn stream