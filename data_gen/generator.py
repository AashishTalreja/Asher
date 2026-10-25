"""
Data Generator for Cyber Hackathon 2026.

Generates realistic synthetic datasets for cyber fraud detection:
- accounts.csv: Core banking account records.
- transactions.csv: Transaction logs (UPI, IMPS, NEFT, ATM).
- complaints.csv: NCRP cyber fraud complaints with free-text narratives.
- entities.csv: Graph entities (shared phone numbers, devices, IP addresses).

Supports deterministic generation (seed=42) matching specifications in:
- docs/08-DATA-MODEL.md
- docs/09-DETECTION-PIPELINE.md
- docs/13-DEMO-SCRIPT.md
"""

import argparse
import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Master Reference Lists & Constants
# ---------------------------------------------------------------------------

BIHAR_DISTRICTS = [
    "Patna",
    "Gaya",
    "Muzaffarpur",
    "Nalanda",
    "Bhagalpur",
    "Darbhanga",
    "Begusarai",
    "Vaishali",
    "Purnia",
    "Rohtas",
    "Samastipur",
    "Saran",
]

FIRST_NAMES = [
    "Rahul", "Amit", "Vikas", "Rohit", "Priya", "Anjali", "Deepak", "Suresh",
    "Pooja", "Neha", "Rajesh", "Manoj", "Rakesh", "Manish", "Abhishek", "Alok",
    "Saurabh", "Sunita", "Kavita", "Rekha", "Sanjay", "Sunil", "Ajay", "Vijay",
    "Sandeep", "Pankaj", "Ravi", "Nitin", "Gaurav", "Arvind", "Ankit", "Shubham",
    "Vivek", "Pratibha", "Shweta", "Archana", "Priyanka", "Jyoti", "Aarti", "Mohan",
    "Mukesh", "Dharmendra", "Santosh", "Bablu", "Chhotu", "Jitendra", "Sonu",
    "Monu", "Chandan", "Kundan", "Roshan", "Shailesh", "Pawan", "Satish", "Ashok",
    "Ramesh", "Dinesh", "Naresh", "Mahesh", "Kishore", "Anand", "Bikram", "Guddu"
]

LAST_NAMES = [
    "Kumar", "Singh", "Sharma", "Verma", "Yadav", "Mishra", "Gupta", "Jha",
    "Pandey", "Prasad", "Choudhary", "Thakur", "Sinha", "Paswan", "Sah",
    "Mandal", "Das", "Shah", "Tiwari", "Rai", "Ojha", "Shukla", "Dubey",
    "Pathak", "Dwivedi", "Tripathy", "Keshri", "Barnwal", "Rawat", "Kashyap"
]

BANK_BRANCHES = {
    "SBI": ["SBIN0001234", "SBIN0002145", "SBIN0003456", "SBIN0004567", "SBIN0005678"],
    "PNB": ["PUNB0014520", "PUNB0023400", "PUNB0034500", "PUNB0045600"],
    "HDFC": ["HDFC0001890", "HDFC0002341", "HDFC0003452", "HDFC0004563"],
    "ICICI": ["ICIC0000876", "ICIC0001234", "ICIC0002345", "ICIC0003456"],
    "BOB": ["BARB0PATNAX", "BARB0NALAND", "BARB0GAYAAX", "BARB0MUZAFF"],
    "CANARA": ["CNRB0001099", "CNRB0002345", "CNRB0003456"],
    "AXIS": ["UTIB0002341", "UTIB0003456", "UTIB0004567"],
}

FRAUD_TYPES = ["JOB_FRAUD", "INVESTMENT", "UPI_FRAUD", "LOAN_APP"]


def format_iso_timestamp(dt: datetime) -> str:
    """Format datetime as ISO string with Indian Standard Time (+05:30)."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S+05:30")


# ---------------------------------------------------------------------------
# 12-Account Mule Ring Specification
# ---------------------------------------------------------------------------

RING_ACCOUNTS = [
    # Mule-1: Primary Inflow Hub / Layer 1 (Rahul Kumar)
    {
        "account_id": "ACC-22451",
        "holder_name": "Rahul Kumar",
        "age_days": 115,
        "kyc_status": "MINIMAL",
        "district": "Patna",
        "bank": "SBI",
        "branch": "SBIN0001234",
        "phone": "+91-9812345678",
        "device_id": "DEV-a8f3e2",
        "ip": "203.0.113.42",
        "opening_date": "2026-07-02",
        "role": "mule_inflow",
    },
    # Mule-2: Layer 2 intermediary in Gaya
    {
        "account_id": "ACC-10033",
        "holder_name": "Amit Kumar",
        "age_days": 62,
        "kyc_status": "MINIMAL",
        "district": "Gaya",
        "bank": "PNB",
        "branch": "PUNB0014520",
        "phone": "+91-9812345678",      # Shared Phone #1
        "device_id": "DEV-a8f3e2",      # Shared Device #1
        "ip": "203.0.113.43",
        "opening_date": "2026-08-24",
        "role": "mule_hop",
    },
    # Mule-3: Layer 3 intermediary in Muzaffarpur
    {
        "account_id": "ACC-99810",
        "holder_name": "Vikas Singh",
        "age_days": 45,
        "kyc_status": "MINIMAL",
        "district": "Muzaffarpur",
        "bank": "BOB",
        "branch": "BARB0MUZAFF",
        "phone": "+91-9812345678",      # Shared Phone #1 (3 accounts share phone)
        "device_id": "DEV-a8f3e2",      # Shared Device #1 (4 accounts share device)
        "ip": "203.0.113.44",
        "opening_date": "2026-09-10",
        "role": "mule_cashout",
    },
    # Mule-4: Parallel branch in Patna
    {
        "account_id": "ACC-10034",
        "holder_name": "Rakesh Verma",
        "age_days": 78,
        "kyc_status": "MINIMAL",
        "district": "Patna",
        "bank": "ICICI",
        "branch": "ICIC0000876",
        "phone": "+91-9876543210",      # Shared Phone #2
        "device_id": "DEV-a8f3e2",      # Shared Device #1 (4th account on DEV-a8f3e2)
        "ip": "203.0.113.45",
        "opening_date": "2026-08-08",
        "role": "mule_hop",
    },
    # Mule-5: Nalanda intermediary
    {
        "account_id": "ACC-10035",
        "holder_name": "Suresh Yadav",
        "age_days": 55,
        "kyc_status": "MINIMAL",
        "district": "Nalanda",
        "bank": "SBI",
        "branch": "SBIN0002145",
        "phone": "+91-9876543210",      # Shared Phone #2
        "device_id": "DEV-b1c2d3",      # Shared Device #2
        "ip": "203.0.113.46",
        "opening_date": "2026-08-31",
        "role": "mule_hop",
    },
    # Mule-6: Nalanda parallel
    {
        "account_id": "ACC-10036",
        "holder_name": "Deepak Mishra",
        "age_days": 89,
        "kyc_status": "MINIMAL",
        "district": "Nalanda",
        "bank": "BOB",
        "branch": "BARB0NALAND",
        "phone": "+91-9876543210",      # Shared Phone #2 (3 accounts share phone)
        "device_id": "DEV-b1c2d3",      # Shared Device #2
        "ip": "203.0.113.47",
        "opening_date": "2026-07-28",
        "role": "mule_hop",
    },
    # Mule-7: Muzaffarpur intermediary
    {
        "account_id": "ACC-10037",
        "holder_name": "Manoj Prasad",
        "age_days": 40,
        "kyc_status": "PENDING",
        "district": "Muzaffarpur",
        "bank": "CANARA",
        "branch": "CNRB0001099",
        "phone": "+91-9823456789",      # Shared Phone #3
        "device_id": "DEV-c3d4e5",      # Shared Device #3
        "ip": "203.0.113.48",
        "opening_date": "2026-09-15",
        "role": "mule_hop",
    },
    # Mule-8: Gaya cash-out
    {
        "account_id": "ACC-10038",
        "holder_name": "Rohit Choudhary",
        "age_days": 35,
        "kyc_status": "PENDING",
        "district": "Gaya",
        "bank": "AXIS",
        "branch": "UTIB0002341",
        "phone": "+91-9823456789",      # Shared Phone #3
        "device_id": "DEV-c3d4e5",      # Shared Device #3
        "ip": "203.0.113.49",
        "opening_date": "2026-09-20",
        "role": "mule_cashout",
    },
    # Mule-9: Patna cash-out / terminal
    {
        "account_id": "ACC-10039",
        "holder_name": "Sunil Paswan",
        "age_days": 50,
        "kyc_status": "MINIMAL",
        "district": "Patna",
        "bank": "SBI",
        "branch": "SBIN0003456",
        "phone": "+91-9823456789",      # Shared Phone #3
        "device_id": "DEV-d4e5f6",      # Shared Device #4
        "ip": "203.0.113.50",
        "opening_date": "2026-09-05",
        "role": "mule_cashout",
    },
    # Recruiter-1: Patna recruiter
    {
        "account_id": "ACC-88001",
        "holder_name": "Rajesh Sinha",
        "age_days": 320,
        "kyc_status": "FULL",
        "district": "Patna",
        "bank": "SBI",
        "branch": "SBIN0001234",
        "phone": "+91-9835012345",
        "device_id": "DEV-d4e5f6",      # Shared Device #4
        "ip": "203.0.113.81",
        "opening_date": "2025-12-09",
        "role": "recruiter",
    },
    # Recruiter-2: Gaya recruiter
    {
        "account_id": "ACC-88002",
        "holder_name": "Alok Thakur",
        "age_days": 280,
        "kyc_status": "FULL",
        "district": "Gaya",
        "bank": "PNB",
        "branch": "PUNB0014520",
        "phone": "+91-9835012346",
        "device_id": "DEV-e5f6a7",
        "ip": "203.0.113.82",
        "opening_date": "2026-01-18",
        "role": "recruiter",
    },
    # Recruiter-3: Muzaffarpur recruiter
    {
        "account_id": "ACC-88003",
        "holder_name": "Sanjay Gupta",
        "age_days": 410,
        "kyc_status": "FULL",
        "district": "Muzaffarpur",
        "bank": "HDFC",
        "branch": "HDFC0001890",
        "phone": "+91-9835012347",
        "device_id": "DEV-e5f6a7",
        "ip": "203.0.113.83",
        "opening_date": "2025-09-10",
        "role": "recruiter",
    },
]


# ---------------------------------------------------------------------------
# 23 Authentic NCRP Complaints
# ---------------------------------------------------------------------------

FIXED_COMPLAINTS = [
    # 7 Linked directly to ACC-22451 (Rahul Kumar) totaling ₹4,90,000 across Patna & Nalanda
    {
        "complaint_id": "NCRP-2026-3812",
        "victim_account": "ACC-5510",
        "beneficiary_upi": "rahul***@ybl",
        "beneficiary_name": "Rahul Kumar",
        "amount": 47000.00,
        "complaint_date": "2026-10-25",
        "district": "Patna",
        "fraud_type": "JOB_FRAUD",
        "text": "₹5000 bheja, rahul***@ybl ko job ke liye, fir 42000 aur manga task complete karne ke liye.",
    },
    {
        "complaint_id": "NCRP-2026-3813",
        "victim_account": "ACC-5511",
        "beneficiary_upi": "rahul.kumar@ybl",
        "beneficiary_name": "Rahul Kumar",
        "amount": 100000.00,
        "complaint_date": "2026-10-25",
        "district": "Patna",
        "fraud_type": "INVESTMENT",
        "text": "High return crypto trading investment: sent ₹1,00,000 to Rahul Kumar on UPI rahul.kumar@ybl.",
    },
    {
        "complaint_id": "NCRP-2026-3814",
        "victim_account": "ACC-5512",
        "beneficiary_upi": "rahul***@ybl",
        "beneficiary_name": "Rahul Kr",
        "amount": 65000.00,
        "complaint_date": "2026-10-24",
        "district": "Nalanda",
        "fraud_type": "JOB_FRAUD",
        "text": "Work from home part-time registration fee ₹65000 sent to rahul***@ybl via phonepe.",
    },
    {
        "complaint_id": "NCRP-2026-3815",
        "victim_account": "ACC-5513",
        "beneficiary_upi": "rahul.k@ybl",
        "beneficiary_name": "Rahul Kumar",
        "amount": 55000.00,
        "complaint_date": "2026-10-25",
        "district": "Patna",
        "fraud_type": "UPI_FRAUD",
        "text": "Electricity bill disconnection fraud: ₹55000 debited to rahul.k@ybl after clicking apk link.",
    },
    {
        "complaint_id": "NCRP-2026-3816",
        "victim_account": "ACC-5514",
        "beneficiary_upi": "rahul***@ybl",
        "beneficiary_name": "R Kumar",
        "amount": 80000.00,
        "complaint_date": "2026-10-25",
        "district": "Nalanda",
        "fraud_type": "INVESTMENT",
        "text": "Telegram VIP trading group: ₹80000 paid to beneficiary rahul***@ybl for double returns.",
    },
    {
        "complaint_id": "NCRP-2026-3817",
        "victim_account": "ACC-5515",
        "beneficiary_upi": "rahul.kumar@ybl",
        "beneficiary_name": "Rahul Kumar",
        "amount": 73000.00,
        "complaint_date": "2026-10-25",
        "district": "Patna",
        "fraud_type": "JOB_FRAUD",
        "text": "YouTube video like rating task scam: transferred ₹73000 to rahul.kumar@ybl over 4 transactions.",
    },
    {
        "complaint_id": "NCRP-2026-3818",
        "victim_account": "ACC-5516",
        "beneficiary_upi": "rahul***@ybl",
        "beneficiary_name": "Rahul Kumar",
        "amount": 70000.00,
        "complaint_date": "2026-10-25",
        "district": "Patna",
        "fraud_type": "LOAN_APP",
        "text": "Instant loan app processing charge and advance EMI: ₹70000 sent to rahul***@ybl.",
    },
    # 16 complaints linking to the rest of the 12-account mule ring (totaling ₹3,80,000)
    # Grand total across all 23 complaints = exactly ₹8,70,000 (₹8.7 Lakh)
    {
        "complaint_id": "NCRP-2026-3819",
        "victim_account": "ACC-5517",
        "beneficiary_upi": "amit.k@paytm",
        "beneficiary_name": "Amit Kumar",
        "amount": 25000.00,
        "complaint_date": "2026-10-24",
        "district": "Gaya",
        "fraud_type": "UPI_FRAUD",
        "text": "Lottery prize processing fee: ₹25,000 sent to Amit Kumar amit.k@paytm.",
    },
    {
        "complaint_id": "NCRP-2026-3820",
        "victim_account": "ACC-5518",
        "beneficiary_upi": "amit***@paytm",
        "beneficiary_name": "Amit Kumar",
        "amount": 30000.00,
        "complaint_date": "2026-10-25",
        "district": "Gaya",
        "fraud_type": "JOB_FRAUD",
        "text": "Part-time data entry job deposit: ₹30,000 sent to amit***@paytm.",
    },
    {
        "complaint_id": "NCRP-2026-3821",
        "victim_account": "ACC-5519",
        "beneficiary_upi": "vikas.singh@okhdfcbank",
        "beneficiary_name": "Vikas Singh",
        "amount": 28000.00,
        "complaint_date": "2026-10-24",
        "district": "Muzaffarpur",
        "fraud_type": "INVESTMENT",
        "text": "Forex trading app: ₹28,000 deposited to Vikas Singh vikas.singh@okhdfcbank.",
    },
    {
        "complaint_id": "NCRP-2026-3822",
        "victim_account": "ACC-5520",
        "beneficiary_upi": "vikas***@okhdfcbank",
        "beneficiary_name": "Vikas Singh",
        "amount": 20000.00,
        "complaint_date": "2026-10-25",
        "district": "Muzaffarpur",
        "fraud_type": "LOAN_APP",
        "text": "Fast cash loan processing fee of ₹20,000 paid to vikas***@okhdfcbank.",
    },
    {
        "complaint_id": "NCRP-2026-3823",
        "victim_account": "ACC-5521",
        "beneficiary_upi": "rakesh.v@icici",
        "beneficiary_name": "Rakesh Verma",
        "amount": 25000.00,
        "complaint_date": "2026-10-23",
        "district": "Patna",
        "fraud_type": "JOB_FRAUD",
        "text": "Online hotel review task fraud: ₹25,000 transferred to Rakesh Verma.",
    },
    {
        "complaint_id": "NCRP-2026-3824",
        "victim_account": "ACC-5522",
        "beneficiary_upi": "rakesh***@icici",
        "beneficiary_name": "Rakesh Verma",
        "amount": 18000.00,
        "complaint_date": "2026-10-24",
        "district": "Patna",
        "fraud_type": "UPI_FRAUD",
        "text": "Fake customer care helpline: ₹18,000 debited to rakesh***@icici.",
    },
    {
        "complaint_id": "NCRP-2026-3825",
        "victim_account": "ACC-5523",
        "beneficiary_upi": "suresh.yadav@sbi",
        "beneficiary_name": "Suresh Yadav",
        "amount": 29000.00,
        "complaint_date": "2026-10-24",
        "district": "Nalanda",
        "fraud_type": "INVESTMENT",
        "text": "Daily interest double money scheme: ₹29,000 sent to Suresh Yadav on UPI.",
    },
    {
        "complaint_id": "NCRP-2026-3826",
        "victim_account": "ACC-5524",
        "beneficiary_upi": "deepak.m@bob",
        "beneficiary_name": "Deepak Mishra",
        "amount": 22000.00,
        "complaint_date": "2026-10-23",
        "district": "Nalanda",
        "fraud_type": "JOB_FRAUD",
        "text": "Typing work registration fee ₹22,000 to deepak.m@bob.",
    },
    {
        "complaint_id": "NCRP-2026-3827",
        "victim_account": "ACC-5525",
        "beneficiary_upi": "manoj.prasad@cnrb",
        "beneficiary_name": "Manoj Prasad",
        "amount": 28500.00,
        "complaint_date": "2026-10-25",
        "district": "Muzaffarpur",
        "fraud_type": "LOAN_APP",
        "text": "Credit card limit upgrade charges: ₹28,500 paid to Manoj Prasad.",
    },
    {
        "complaint_id": "NCRP-2026-3828",
        "victim_account": "ACC-5526",
        "beneficiary_upi": "rohit.c@axis",
        "beneficiary_name": "Rohit Choudhary",
        "amount": 19000.00,
        "complaint_date": "2026-10-24",
        "district": "Gaya",
        "fraud_type": "INVESTMENT",
        "text": "Stock market advisory tips fraud: ₹19,000 paid to rohit.c@axis.",
    },
    {
        "complaint_id": "NCRP-2026-3829",
        "victim_account": "ACC-5527",
        "beneficiary_upi": "sunil.p@sbi",
        "beneficiary_name": "Sunil Paswan",
        "amount": 26000.00,
        "complaint_date": "2026-10-25",
        "district": "Patna",
        "fraud_type": "JOB_FRAUD",
        "text": "Airport ground staff recruitment deposit: ₹26,000 transferred to sunil.p@sbi.",
    },
    {
        "complaint_id": "NCRP-2026-3830",
        "victim_account": "ACC-5528",
        "beneficiary_upi": "rajesh.sinha@ybl",
        "beneficiary_name": "Rajesh Sinha",
        "amount": 15000.00,
        "complaint_date": "2026-10-22",
        "district": "Patna",
        "fraud_type": "UPI_FRAUD",
        "text": "Online marketplace army officer vehicle advance: ₹15,000 sent to Rajesh Sinha.",
    },
    {
        "complaint_id": "NCRP-2026-3831",
        "victim_account": "ACC-5529",
        "beneficiary_upi": "alok.thakur@paytm",
        "beneficiary_name": "Alok Thakur",
        "amount": 22000.00,
        "complaint_date": "2026-10-23",
        "district": "Gaya",
        "fraud_type": "JOB_FRAUD",
        "text": "Government job interview security deposit ₹22,000 sent to Alok Thakur.",
    },
    {
        "complaint_id": "NCRP-2026-3832",
        "victim_account": "ACC-5530",
        "beneficiary_upi": "sanjay.gupta@okhdfcbank",
        "beneficiary_name": "Sanjay Gupta",
        "amount": 29999.00,
        "complaint_date": "2026-10-24",
        "district": "Muzaffarpur",
        "fraud_type": "INVESTMENT",
        "text": "Commodity gold trading group: sent ₹29,999 to Sanjay Gupta.",
    },
    {
        "complaint_id": "NCRP-2026-3833",
        "victim_account": "ACC-5531",
        "beneficiary_upi": "suresh.y@sbi",
        "beneficiary_name": "Suresh Yadav",
        "amount": 26501.00,
        "complaint_date": "2026-10-25",
        "district": "Nalanda",
        "fraud_type": "JOB_FRAUD",
        "text": "Telegram prepaid order completion task: ₹26,501 transferred to suresh.y@sbi.",
    },
    {
        "complaint_id": "NCRP-2026-3834",
        "victim_account": "ACC-5532",
        "beneficiary_upi": "amit.kumar@paytm",
        "beneficiary_name": "Amit Kumar",
        "amount": 16000.00,
        "complaint_date": "2026-10-25",
        "district": "Gaya",
        "fraud_type": "UPI_FRAUD",
        "text": "e-KYC biometric update phishing message: ₹16,000 sent to Amit Kumar.",
    },
]


# ---------------------------------------------------------------------------
# Background Accounts & Transactions Generator
# ---------------------------------------------------------------------------

def generate_background_accounts(n_accounts: int = 500, seed: int = 42, start_id: int = 1) -> list[dict]:
    """Generate authentic normal background accounts."""
    rng = np.random.default_rng(seed)
    accounts = []
    base_date = datetime(2026, 10, 25)

    kyc_choices = ["FULL", "MINIMAL", "PENDING"]
    kyc_probs = [0.85, 0.12, 0.03]
    banks = list(BANK_BRANCHES.keys())

    for i in range(n_accounts):
        acct_id = f"ACC-{start_id + i:05d}"
        first_name = rng.choice(FIRST_NAMES)
        last_name = rng.choice(LAST_NAMES)
        holder_name = f"{first_name} {last_name}"

        age_days = int(rng.integers(30, 1800))
        opening_date = (base_date - timedelta(days=age_days)).strftime("%Y-%m-%d")
        kyc = rng.choice(kyc_choices, p=kyc_probs)
        district = rng.choice(BIHAR_DISTRICTS)
        bank = rng.choice(banks)
        branch = rng.choice(BANK_BRANCHES[bank])

        phone_num = 9000000000 + int(rng.integers(100000000, 999999999))
        phone = f"+91-{phone_num}"
        dev_hex = f"{rng.integers(0x100000, 0xFFFFFF):06x}"
        device_id = f"DEV-{dev_hex}"
        ip = f"103.{rng.integers(10, 250)}.{rng.integers(1, 254)}.{rng.integers(1, 254)}"

        accounts.append({
            "account_id": acct_id,
            "holder_name": holder_name,
            "age_days": age_days,
            "kyc_status": kyc,
            "district": district,
            "bank": bank,
            "branch": branch,
            "phone": phone,
            "device_id": device_id,
            "ip": ip,
            "opening_date": opening_date,
            "role": "normal",
        })

    return accounts


def generate_ring_transactions(base_time: datetime) -> list[dict]:
    """
    Generate transactions for the 12-account ring:
    1. Historical 90-day baseline for ACC-22451 (2 txns/day @ ~₹500).
    2. Recruiter seed transactions (3 recruiters -> 9 mules @ ₹500 45 days ago).
    3. Today's fraud burst: 47 transactions @ ₹9,999 + ₹10,000 from victim accounts into ACC-22451.
    4. Rapid Layering Trail (< 10 min gaps, > 85% pass-through):
       ACC-22451 (Patna) -> ACC-10033 (Gaya) -> ACC-99810 (Muzaffarpur) -> ATM Cash-outs
       and parallel branch via ACC-10034 -> ACC-10035 -> ACC-10036 -> ACC-10037.
    """
    txns = []
    txn_counter = 1

    # 1. Historical baseline for ACC-22451: ~2 txns/day @ ~₹500 for 60 days
    # This ensures a strong, measurable 23-sigma baseline deviation
    for day_offset in range(60, 0, -1):
        day_date = base_time - timedelta(days=day_offset)
        # txn 1 (morning)
        t1 = day_date.replace(hour=9, minute=15, second=0)
        amt1 = round(float(np.random.normal(500, 25)), 2)
        if amt1 < 100:
            amt1 = 500.00
        txns.append({
            "txn_id": f"TXN-{txn_counter:08d}",
            "from_account": "ACC-22451",
            "to_account": "ACC-00015",
            "amount": amt1,
            "timestamp": format_iso_timestamp(t1),
            "channel": "UPI",
            "district": "Patna",
        })
        txn_counter += 1

        # txn 2 (evening)
        t2 = day_date.replace(hour=18, minute=45, second=0)
        amt2 = round(float(np.random.normal(500, 25)), 2)
        if amt2 < 100:
            amt2 = 500.00
        txns.append({
            "txn_id": f"TXN-{txn_counter:08d}",
            "from_account": "ACC-22451",
            "to_account": "ACC-00028",
            "amount": amt2,
            "timestamp": format_iso_timestamp(t2),
            "channel": "UPI",
            "district": "Patna",
        })
        txn_counter += 1

    # 2. Recruiter Onboarding Seed Credits (Flow 3 in scenario: ₹500 from recruiter)
    recruit_time = base_time - timedelta(days=45, hours=4)
    recruiter_map = {
        "ACC-88001": ["ACC-22451", "ACC-10034", "ACC-10039"],
        "ACC-88002": ["ACC-10033", "ACC-10035", "ACC-10038"],
        "ACC-88003": ["ACC-99810", "ACC-10036", "ACC-10037"],
    }
    for rec_id, mules in recruiter_map.items():
        for m_id in mules:
            txns.append({
                "txn_id": f"TXN-{txn_counter:08d}",
                "from_account": rec_id,
                "to_account": m_id,
                "amount": 500.00,
                "timestamp": format_iso_timestamp(recruit_time),
                "channel": "IMPS",
                "district": "Patna",
            })
            txn_counter += 1
            recruit_time += timedelta(minutes=7)

    # 3. Fraud Inflow Burst on 2026-10-25 into ACC-22451 (Total ~₹4.9L, 47 txns @ ₹9,999)
    inflow_start = base_time.replace(hour=9, minute=30, second=0)
    victim_pool = [c["victim_account"] for c in FIXED_COMPLAINTS] + [f"ACC-{i:05d}" for i in range(100, 130)]

    for i in range(47):
        inflow_t = inflow_start + timedelta(minutes=int(i * 2.2))
        victim_acct = victim_pool[i % len(victim_pool)]
        txns.append({
            "txn_id": f"TXN-{txn_counter:08d}",
            "from_account": victim_acct,
            "to_account": "ACC-22451",
            "amount": 9999.00,
            "timestamp": format_iso_timestamp(inflow_t),
            "channel": "UPI",
            "district": "Patna",
        })
        txn_counter += 1

    # Add two round amount transactions to push total to ~₹4.90L
    for extra_amt in [10000.00, 10047.00]:
        inflow_t = base_time.replace(hour=11, minute=28, second=0) if extra_amt == 10000.00 else base_time.replace(hour=11, minute=30, second=0)
        txns.append({
            "txn_id": f"TXN-{txn_counter:08d}",
            "from_account": "ACC-5510",
            "to_account": "ACC-22451",
            "amount": extra_amt,
            "timestamp": format_iso_timestamp(inflow_t),
            "channel": "UPI",
            "district": "Patna",
        })
        txn_counter += 1

    # 4. Rapid Layering Trail (< 10 min hop latency, > 85% pass-through):
    # Branch A: ACC-22451 (Patna) -> ACC-10033 (Gaya) -> ACC-99810 (Muzaffarpur) -> ATM Cash-out
    layer_t = base_time.replace(hour=11, minute=32, second=0)

    # Hop 1: ACC-22451 -> ACC-10033 (Gaya) - 5 structured transactions of ₹49,000 / ₹45,000
    for amt in [49000.00, 49000.00, 49000.00, 49000.00, 45000.00]:
        txns.append({
            "txn_id": f"TXN-{txn_counter:08d}",
            "from_account": "ACC-22451",
            "to_account": "ACC-10033",
            "amount": amt,
            "timestamp": format_iso_timestamp(layer_t),
            "channel": "UPI",
            "district": "Patna",
        })
        txn_counter += 1
        layer_t += timedelta(seconds=70)

    # Hop 1b: ACC-22451 -> ACC-10034 (Patna parallel) - 4 structured transactions
    layer_t = base_time.replace(hour=11, minute=34, second=0)
    for amt in [49000.00, 49000.00, 49000.00, 49000.00]:
        txns.append({
            "txn_id": f"TXN-{txn_counter:08d}",
            "from_account": "ACC-22451",
            "to_account": "ACC-10034",
            "amount": amt,
            "timestamp": format_iso_timestamp(layer_t),
            "channel": "UPI",
            "district": "Patna",
        })
        txn_counter += 1
        layer_t += timedelta(seconds=65)

    # Hop 2: ACC-10033 (Gaya) -> ACC-99810 (Muzaffarpur) - within 5 minutes of receipt
    layer_t = base_time.replace(hour=11, minute=41, second=0)
    for amt in [49000.00, 49000.00, 49000.00, 49000.00, 40000.00]:
        txns.append({
            "txn_id": f"TXN-{txn_counter:08d}",
            "from_account": "ACC-10033",
            "to_account": "ACC-99810",
            "amount": amt,
            "timestamp": format_iso_timestamp(layer_t),
            "channel": "IMPS",
            "district": "Gaya",
        })
        txn_counter += 1
        layer_t += timedelta(seconds=75)

    # Hop 3: ACC-99810 (Muzaffarpur) -> ATM Cash-outs (Total cashout in 20 min from entry!)
    layer_t = base_time.replace(hour=11, minute=50, second=0)
    for amt in [49000.00, 49000.00, 49000.00, 49000.00, 35000.00]:
        txns.append({
            "txn_id": f"TXN-{txn_counter:08d}",
            "from_account": "ACC-99810",
            "to_account": "ATM-MZR-01",
            "amount": amt,
            "timestamp": format_iso_timestamp(layer_t),
            "channel": "ATM",
            "district": "Muzaffarpur",
        })
        txn_counter += 1
        layer_t += timedelta(seconds=80)

    # Branch B: ACC-10034 -> ACC-10035 (Nalanda) -> ACC-10036 (Nalanda) -> ACC-10037 (Muzaffarpur) -> ATM
    layer_t = base_time.replace(hour=11, minute=43, second=0)
    for amt in [49000.00, 49000.00, 49000.00, 45000.00]:
        txns.append({
            "txn_id": f"TXN-{txn_counter:08d}",
            "from_account": "ACC-10034",
            "to_account": "ACC-10035",
            "amount": amt,
            "timestamp": format_iso_timestamp(layer_t),
            "channel": "IMPS",
            "district": "Patna",
        })
        txn_counter += 1
        layer_t += timedelta(seconds=60)

    layer_t = base_time.replace(hour=11, minute=48, second=0)
    for amt in [49000.00, 49000.00, 49000.00, 40000.00]:
        txns.append({
            "txn_id": f"TXN-{txn_counter:08d}",
            "from_account": "ACC-10035",
            "to_account": "ACC-10036",
            "amount": amt,
            "timestamp": format_iso_timestamp(layer_t),
            "channel": "IMPS",
            "district": "Nalanda",
        })
        txn_counter += 1
        layer_t += timedelta(seconds=60)

    layer_t = base_time.replace(hour=11, minute=53, second=0)
    for amt in [49000.00, 49000.00, 49000.00, 35000.00]:
        txns.append({
            "txn_id": f"TXN-{txn_counter:08d}",
            "from_account": "ACC-10036",
            "to_account": "ACC-10037",
            "amount": amt,
            "timestamp": format_iso_timestamp(layer_t),
            "channel": "IMPS",
            "district": "Nalanda",
        })
        txn_counter += 1
        layer_t += timedelta(seconds=60)

    layer_t = base_time.replace(hour=11, minute=58, second=0)
    for amt in [49000.00, 49000.00, 45000.00]:
        txns.append({
            "txn_id": f"TXN-{txn_counter:08d}",
            "from_account": "ACC-10037",
            "to_account": "ATM-PAT-04",
            "amount": amt,
            "timestamp": format_iso_timestamp(layer_t),
            "channel": "ATM",
            "district": "Muzaffarpur",
        })
        txn_counter += 1
        layer_t += timedelta(seconds=60)

    return txns


def generate_background_transactions(
    bg_accounts: list[dict],
    target_count: int = 4750,
    seed: int = 42,
    base_time: datetime = datetime(2026, 10, 25, 12, 0, 0),
) -> list[dict]:
    """Generate realistic background transactions across normal accounts."""
    rng = np.random.default_rng(seed)
    txns = []
    acct_ids = [a["account_id"] for a in bg_accounts]
    districts = [a["district"] for a in bg_accounts]

    # Pre-generate monthly salary credits for background accounts
    # Happens on 1st-5th of previous months
    for month_back in [1, 2]:
        for i in range(0, len(acct_ids), 2):
            sal_day = int(rng.integers(1, 6))
            sal_date = (base_time - timedelta(days=month_back * 30)).replace(
                day=sal_day, hour=10, minute=rng.integers(10, 50), second=0
            )
            sal_amt = round(float(rng.choice([25000, 35000, 45000, 60000, 75000])), 2)
            txns.append({
                "from_account": "CORP-PAYROLL-01",
                "to_account": acct_ids[i],
                "amount": sal_amt,
                "timestamp": format_iso_timestamp(sal_date),
                "channel": rng.choice(["NEFT", "IMPS"]),
                "district": districts[i],
            })

    # Day-to-day transactions across the last 90 days
    remaining_txns = target_count - len(txns)
    if remaining_txns > 0:
        for _ in range(remaining_txns):
            # Pick day in past 90 days
            day_offset = int(rng.integers(0, 90))
            hour = int(rng.choice([8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]))
            minute = int(rng.integers(0, 60))
            second = int(rng.integers(0, 60))

            t = (base_time - timedelta(days=day_offset)).replace(
                hour=hour, minute=minute, second=second
            )

            idx_from = rng.integers(0, len(acct_ids))
            idx_to = rng.integers(0, len(acct_ids))
            while idx_to == idx_from:
                idx_to = rng.integers(0, len(acct_ids))

            channel = rng.choice(["UPI", "UPI", "UPI", "IMPS", "ATM", "NEFT"])
            if channel == "ATM":
                to_acc = f"ATM-{rng.choice(['PAT', 'GAY', 'MZR', 'NAL'])}-{rng.integers(1, 10):02d}"
                amt = float(rng.choice([500, 1000, 2000, 3000, 5000, 10000]))
            elif channel == "UPI":
                to_acc = acct_ids[idx_to]
                # Typical everyday P2P / P2M amounts
                amt = round(float(rng.exponential(450) + 50), 2)
                if amt > 5000:
                    amt = round(float(rng.integers(100, 2500)), 2)
            else:
                to_acc = acct_ids[idx_to]
                amt = round(float(rng.integers(1000, 15000)), 2)

            txns.append({
                "from_account": acct_ids[idx_from],
                "to_account": to_acc,
                "amount": amt,
                "timestamp": format_iso_timestamp(t),
                "channel": channel,
                "district": districts[idx_from],
            })

    # Sort transactions chronologically
    txns.sort(key=lambda x: x["timestamp"])

    # Re-assign IDs in order
    for i, t in enumerate(txns, start=1):
        t["txn_id"] = f"TXN-{i:08d}"

    return txns


# ---------------------------------------------------------------------------
# Entities Extractor
# ---------------------------------------------------------------------------

def build_entities_dataframe(accounts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract shared and individual entities (phones, devices, IPs)
    into entities.csv matching schema in docs/08-DATA-MODEL.md.
    """
    entity_records = []
    entity_id_counter = 1

    # Group by phone
    phone_groups = accounts_df.groupby("phone")["account_id"].apply(list).to_dict()
    # Group by device_id
    dev_groups = accounts_df.groupby("device_id")["account_id"].apply(list).to_dict()
    # Group by IP
    ip_groups = accounts_df.groupby("ip")["account_id"].apply(list).to_dict()

    # Prioritize shared entities (len > 1) first
    for group_type, group_dict in [("phone", phone_groups), ("device", dev_groups), ("ip", ip_groups)]:
        # First shared
        for val, accts in sorted(group_dict.items(), key=lambda x: len(x[1]), reverse=True):
            if len(accts) > 1:
                entity_records.append({
                    "entity_id": f"ENT-{entity_id_counter:04d}",
                    "type": group_type,
                    "value": val,
                    "linked_accounts": "|".join(accts),
                })
                entity_id_counter += 1

    # Next single entities for full graph coverage
    for group_type, group_dict in [("phone", phone_groups), ("device", dev_groups), ("ip", ip_groups)]:
        for val, accts in group_dict.items():
            if len(accts) == 1:
                entity_records.append({
                    "entity_id": f"ENT-{entity_id_counter:04d}",
                    "type": group_type,
                    "value": val,
                    "linked_accounts": accts[0],
                })
                entity_id_counter += 1

    return pd.DataFrame(entity_records)


# ---------------------------------------------------------------------------
# Generator API Functions
# ---------------------------------------------------------------------------

def generate_fixed_case(
    out_dir: str = "data",
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Deterministic seed=42 generator.
    - Exactly 12 mule ring accounts (3 recruiters, 9 mules, rapid layering, shared entities)
    - 500 normal background accounts (Total = 512 accounts)
    - Exactly 23 complaints linking to the ring accounts
    - Rapid layering transactions with < 10 min hop latency and > 85% pass-through
    - entities.csv linking shared phones, devices, and IPs
    """
    os.makedirs(out_dir, exist_ok=True)
    base_time = datetime(2026, 10, 25, 12, 0, 0)

    # 1. Accounts
    bg_accounts = generate_background_accounts(n_accounts=500, seed=seed, start_id=1)
    all_accounts = RING_ACCOUNTS + bg_accounts
    accounts_df = pd.DataFrame(all_accounts)
    # Strip internal 'role' column from saved CSV to match exact schema
    schema_accounts_cols = [
        "account_id", "holder_name", "age_days", "kyc_status", "district",
        "bank", "branch", "phone", "device_id", "ip", "opening_date"
    ]
    accounts_df_csv = accounts_df[schema_accounts_cols].copy()

    # 2. Transactions
    ring_txns = generate_ring_transactions(base_time=base_time)
    bg_txns = generate_background_transactions(
        bg_accounts=bg_accounts,
        target_count=5000 - len(ring_txns),
        seed=seed,
        base_time=base_time,
    )
    all_txns = ring_txns + bg_txns
    all_txns.sort(key=lambda x: x["timestamp"])
    for idx, t in enumerate(all_txns, start=1):
        t["txn_id"] = f"TXN-{idx:08d}"

    txns_df = pd.DataFrame(all_txns)
    schema_txn_cols = [
        "txn_id", "from_account", "to_account", "amount", "timestamp", "channel", "district"
    ]
    txns_df_csv = txns_df[schema_txn_cols].copy()

    # 3. Complaints
    complaints_df = pd.DataFrame(FIXED_COMPLAINTS)
    schema_complaint_cols = [
        "complaint_id", "victim_account", "beneficiary_upi", "beneficiary_name",
        "amount", "complaint_date", "district", "fraud_type", "text"
    ]
    complaints_df_csv = complaints_df[schema_complaint_cols].copy()

    # 4. Entities
    entities_df = build_entities_dataframe(accounts_df_csv)

    # Save to disk with utf-8 encoding
    accounts_df_csv.to_csv(os.path.join(out_dir, "accounts.csv"), index=False, encoding="utf-8")
    txns_df_csv.to_csv(os.path.join(out_dir, "transactions.csv"), index=False, encoding="utf-8")
    complaints_df_csv.to_csv(os.path.join(out_dir, "complaints.csv"), index=False, encoding="utf-8")
    entities_df.to_csv(os.path.join(out_dir, "entities.csv"), index=False, encoding="utf-8")

    return accounts_df_csv, txns_df_csv, complaints_df_csv, entities_df


def generate_all(size: str = "demo", seed: int = 42, out_dir: str = "data") -> None:
    """
    Main entry point: generates CSV files and displays a summary table.
    size: 'demo' (fixed 512 accounts case) or 'scale' (for large scale stress tests).
    """
    print(f"\n=======================================================")
    print(f"  BIHAR CYBER HACKATHON 2026 - SYNTHETIC DATA GENERATOR")
    print(f"=======================================================")
    print(f"[*] Configuration: size='{size}', seed={seed}, out_dir='{out_dir}'")

    acc_df, txn_df, comp_df, ent_df = generate_fixed_case(out_dir=out_dir, seed=seed)

    # Summary Statistics
    tot_comp_amt = comp_df["amount"].sum()
    rahul_comp = comp_df[comp_df["beneficiary_upi"].str.startswith("rahul")]
    rahul_comp_amt = rahul_comp["amount"].sum()
    shared_phones = ent_df[(ent_df["type"] == "phone") & (ent_df["linked_accounts"].str.contains(r"\|"))]
    shared_devices = ent_df[(ent_df["type"] == "device") & (ent_df["linked_accounts"].str.contains(r"\|"))]

    print("\n[+] Data Generation Complete!")
    print("-------------------------------------------------------")
    print(f"  accounts.csv:     {len(acc_df):>6,d} accounts (12 mule ring + 500 background)")
    print(f"  transactions.csv: {len(txn_df):>6,d} transactions")
    print(f"  complaints.csv:   {len(comp_df):>6,d} complaints (totaling Rs. {tot_comp_amt:,.2f})")
    print(f"  entities.csv:     {len(ent_df):>6,d} entities ({len(shared_phones)} shared phones, {len(shared_devices)} shared devices)")
    print("-------------------------------------------------------")
    print("[+] Key Mule Ring & Verification Highlights:")
    print(f"  - Target Mule Inflow Hub: ACC-22451 (Rahul Kumar, Patna)")
    print(f"  - Complaints linked to Rahul Kumar: {len(rahul_comp)} complaints (Rs. {rahul_comp_amt:,.2f})")
    print(f"  - Ring Accounts: 12 (3 recruiters + 9 mules across Patna, Gaya, Muzaffarpur, Nalanda)")
    print(f"  - Layering Trail: ACC-22451 -> ACC-10033 -> ACC-99810 -> ATM Cash-outs (< 20 min)")
    print(f"  - Output Directory: {os.path.abspath(out_dir)}")
    print("=======================================================\n")


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic cyber fraud dataset.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--out", type=str, default="data", help="Output directory for CSV files (default: data)")
    parser.add_argument("--size", type=str, default="demo", choices=["demo", "scale"], help="Dataset size (demo or scale)")
    args = parser.parse_args()

    generate_all(size=args.size, seed=args.seed, out_dir=args.out)
