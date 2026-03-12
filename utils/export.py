"""
utils/export.py
---------------
Responsibility: exporting transactions to CSV format.
"""

import csv
import os
from datetime import datetime
from typing import List

from data.storage import Transaction


def export_csv(transactions: List[Transaction], path: str = None) -> str:
    """
    Export transactions to a CSV file.
    Returns the path to the created file.
    """
    if path is None:
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        path = os.path.expanduser(f"~/budget_export_{date_str}.csv")

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Type", "Amount (EUR)", "Description", "Date"])
        for t in transactions:
            writer.writerow([
                "Income" if t.is_income() else "Expense",
                f"{t.amount:.2f}",
                t.description,
                t.date,
            ])

    return path
