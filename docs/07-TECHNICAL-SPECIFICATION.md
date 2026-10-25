# Technical Specification

## Tech Stack (Locked)

| Layer | Tool | Purpose |
|---|---|---|
| Language | Python 3.11 | Backend + CLI |
| Data | pandas, numpy | Feature engineering |
| ML | XGBoost, scikit-learn | Risk scoring |
| Graph | networkx | Trail, Louvain, centrality |
| NLP/ER | re, rapidfuzz, jellyfish | Entity resolution |
| TUI | rich, prompt_toolkit | Terminal screens |
| Viz | matplotlib | Network PNG export |
| Report | reportlab | PDF generation |
| Hashing | hashlib | SHA-256 evidence |
| Storage | CSV | Portable, gitignore-able |
| VCS | Git + GitHub | Iterative commits |

## Dependencies (`requirements.txt`)

```
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
xgboost>=2.0
networkx>=3.1
rapidfuzz>=3.0
jellyfish>=1.0
rich>=13.0
prompt_toolkit>=3.0
matplotlib>=3.7
reportlab>=4.0
python-dateutil>=2.8
faker>=20.0
```

## Environment Setup

```bash
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # Linux/macOS

pip install -r requirements.txt
```

Tested on:
- Windows 11 + PowerShell (primary)
- Ubuntu 22.04 + bash
- macOS Ventura + zsh

## Entry Points

| Command | Purpose |
|---|---|
| `python -m data_gen.generator --seed 42 --out data/fixed/` | Generate fixed demo case |
| `python -m data_gen.generator --seed 999 --out data/random/` | Generate random dataset |
| `python -m cli.menu --data-dir data/fixed/` | Launch terminal UI |

## Configuration

Config lives in `core/config.py`:

```python
FUSION_WEIGHTS = {
    'rule': 0.20,
    'baseline': 0.20,
    'ml': 0.35,
    'complaint': 0.15,
    'graph': 0.10,
}
TIER_THRESHOLDS = {'CRITICAL': 80, 'HIGH': 60, 'MEDIUM': 40}
MAX_HOPS = 5
TXN_WINDOW_HOURS = 24
BASELINE_DAYS = 90
```

## Module Contracts

### `core/rules.py`

```python
def evaluate(account_id: str, ctx: dict) -> dict:
    """
    Returns:
      {
        'fired': [{'rule': str, 'weight': float, 'evidence': str}, ...],
        'score': float  # 0..1
      }
    """
```

### `core/baseline.py`

```python
def deviation(account_id: str, as_of: datetime, ctx: dict) -> dict:
    """
    Returns:
      {
        'score': float,  # 0..1
        'z_amt': float, 'z_freq': float,
        'new_counterparty': bool,
        'dormancy_break': bool,
        'explanation': str
      }
    """
```

### `core/ml.py`

```python
def train(txns: pd.DataFrame, labels: pd.Series) -> None:
    """Trains and saves model to models/xgb.pkl"""

def predict(account_id: str, ctx: dict) -> dict:
    """
    Returns:
      {
        'score': float,  # probability 0..1
        'top_features': [(name, importance), ...],
        'confidence': 'low' | 'normal'
      }
    """
```

### `core/complaints.py`

```python
def resolve(query: str, ctx: dict) -> list[dict]:
    """Returns matched accounts with confidence."""

def linked(account_id: str, ctx: dict) -> list[dict]:
    """Returns complaints linked to this account."""

def clusters(ctx: dict) -> list[dict]:
    """Returns incident clusters (same beneficiary / shared entity)."""
```

### `core/graph_ops.py`

```python
def trace(origin: str, max_hops: int = 5, window_hours: int = 24) -> dict:
    """
    Returns:
      {
        'paths': [...],
        'chain_type': 'LAYERING'|'FAN_OUT'|'FAN_IN'|'CIRCULAR'|'STRUCTURING',
        'intermediaries': [(acct, pass_through_ratio), ...],
        'cash_out_points': [...]
      }
    """

def rings(ctx: dict) -> list[dict]:
    """Returns Louvain communities scored for suspicion."""
```

### `core/fusion.py`

```python
def score(account_id: str, ctx: dict) -> dict:
    """
    Returns:
      {
        'score': float,  # 0..100
        'tier': 'CRITICAL'|'HIGH'|'MEDIUM'|'LOW',
        'contributions': {rule, baseline, ml, complaint, graph},
        'confidence': 'low'|'normal',
        'explanation': str
      }
    """

def score_history(account_id: str) -> list[dict]:
    """Returns append-only score log entries."""
```

### `core/report.py`

```python
def generate_pdf(account_id: str, ctx: dict, out_path: str) -> dict:
    """
    Returns:
      {
        'path': str,
        'sha256': str,
        'generated_at': ISO8601,
        'case_ref': str
      }
    """
```

## Performance Targets

| Operation | Target | Measured on |
|---|---|---|
| Score lookup | < 200 ms | 2K-account dataset |
| Money trail (5 hops) | < 5 s | 2K-account dataset |
| Louvain on 2K nodes | < 3 s | — |
| PDF generation | < 10 s | — |
| Full startup | < 5 s | Warm data cache |

## Error Handling

- Missing account → return `{'error': 'ACCOUNT_NOT_FOUND'}`
- Empty complaint matches → return empty list, not exception
- Cold-start account (age < 90d) → ML returns `confidence: 'low'`, fall back to rule + deviation
- Malformed CSV → fail fast with clear error message on startup