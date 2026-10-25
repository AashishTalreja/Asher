# Data Model

## Entity Schemas

### `accounts.csv`

| Column | Type | Example |
|---|---|---|
| account_id | str | `ACC-22451` |
| holder_name | str | `Rahul Kumar` |
| age_days | int | `47` |
| kyc_status | enum | `FULL` / `MINIMAL` / `PENDING` |
| district | str | `Patna` |
| bank | str | `SBI` |
| branch | str | `SBI0001234` |
| phone | str | `+91-9812345678` |
| device_id | str | `DEV-a8f3e2` |
| ip | str | `203.0.113.42` |
| opening_date | ISO | `2026-09-05` |

### `transactions.csv`

| Column | Type | Example |
|---|---|---|
| txn_id | str | `TXN-00012345` |
| from_account | str | `ACC-22451` |
| to_account | str | `ACC-10033` |
| amount | float | `9999.00` |
| timestamp | ISO | `2026-10-25T14:32:00+05:30` |
| channel | enum | `UPI` / `IMPS` / `NEFT` / `ATM` |
| district | str | `Patna` |

### `complaints.csv`

| Column | Type | Example |
|---|---|---|
| complaint_id | str | `NCRP-2026-3812` |
| victim_account | str | `ACC-5510` |
| beneficiary_upi | str | `rahul***@ybl` |
| beneficiary_name | str | `Rahul Kumar` |
| amount | float | `47000.00` |
| complaint_date | ISO | `2026-11-02` |
| district | str | `Patna` |
| fraud_type | enum | `JOB_FRAUD` / `INVESTMENT` / `UPI_FRAUD` / `LOAN_APP` |
| text | str | `"₹5000 bheja, rahul***@ybl ko job ke liye"` |

### `entities.csv`

| Column | Type | Example |
|---|---|---|
| entity_id | str | `ENT-0001` |
| type | enum | `phone` / `device` / `ip` |
| value | str | `+91-9812345678` |
| linked_accounts | str (pipe-sep) | `ACC-22451\|ACC-10033\|ACC-9981` |

## Dataset Sizes

| Dataset | Accounts | Txns | Complaints | Purpose |
|---|---|---|---|---|
| Fixed case (`seed=42`) | 512 (12 ring + 500 bg) | 5,000 | 23 | Main demo |
| Random demo | 2,000 | 20,000 | 500 | Alternate test |
| Scale test (optional) | 50,000 | 500,000 | 5,000 | Performance proof |

## Generator Specification

### `data_gen/generator.py`

```python
def generate_fixed_case(seed=42) -> None:
    """
    Deterministic seed.
    - 12-account mule ring: 3 recruiters -> 9 mules -> 2 cash-outs
    - 4 shared devices, 2 shared phones
    - 23 complaints across Patna, Nalanda, Muzaffarpur
    - ₹8.7L total across complaints
    - 500 background accounts with normal activity
    """

def generate_background(n_accounts=2000, n_txns=20000, seed=42) -> None:
    """
    Normal activity:
    - Salary credits, bill payments, UPI to friends/family
    - Real Indian names via faker-hi + hardcoded list
    - Real IFSC: SBIN0001234, HDFC0005678, etc.
    - Real UPI: <name>@ybl, @paytm, @okhdfcbank
    - Districts: Patna, Gaya, Muzaffarpur, Bhagalpur, Darbhanga
    """

def generate_all(size='demo', seed=42) -> None:
    """size='demo' (2K) or 'scale' (50K)."""
```

## Data Realism Checklist

- [x] Indian names (with Hindi transliteration variants)
- [x] Real IFSC format `XXXX0YYYYYY`
- [x] Real UPI handles
- [x] Real Bihar districts (7+)
- [x] NCRP IDs format `NCRP-2026-XXXXX`
- [x] Mixed Hindi/English complaint text
- [x] Realistic dormancy → burst patterns
- [x] Round-amount transactions (₹9,999 / ₹49,999)
- [x] Structuring below reporting thresholds

## Reproducibility

- All generation uses a **seed** parameter
- Fixed case uses `seed=42` deterministically
- Random tests use different seeds (999, 1234) to validate generality
- CSVs are gitignored (regenerated on demand)