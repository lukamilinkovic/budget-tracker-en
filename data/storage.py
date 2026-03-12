"""
data/storage.py
---------------
Responsibility: reading and writing transactions to disk.
No UI logic here.
"""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

DATA_FILE = "transactions.json"


@dataclass
class Transaction:
    """Model for a single transaction."""
    type: str        # "income" | "expense"
    amount: float
    description: str
    date: str

    @staticmethod
    def create(type: str, amount: float, description: str,
               dt: datetime = None) -> "Transaction":
        """Factory method — creates a new transaction.
        Uses provided dt for the month, but current time for HH:MM."""
        if dt is None:
            dt = datetime.now()
        # Use the provided month/year but current day & time
        now = datetime.now()
        final_dt = dt.replace(day=now.day, hour=now.hour,
                              minute=now.minute, second=now.second)
        return Transaction(
            type=type,
            amount=amount,
            description=description or type.capitalize(),
            date=final_dt.strftime("%d. %m. %Y, %H:%M"),
        )

    def is_income(self) -> bool:
        return self.type == "income"


def load() -> List[Transaction]:
    """Load all transactions from disk."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Transaction(**t) for t in raw]


def save(transactions: List[Transaction]) -> None:
    """Save all transactions to disk."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([asdict(t) for t in transactions],
                  f, ensure_ascii=False, indent=2)


def add(transaction: Transaction) -> List[Transaction]:
    """Add a transaction and save. Returns updated list."""
    all_t = load()
    all_t.append(transaction)
    save(all_t)
    return all_t


def delete(idx: int) -> List[Transaction]:
    """Delete a transaction by index and save. Returns updated list."""
    all_t = load()
    all_t.pop(idx)
    save(all_t)
    return all_t
