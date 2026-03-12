"""
utils/charts.py
---------------
Responsibility: rendering charts with matplotlib -> Kivy Image widget.
No UI layout here — charts only.
"""

import io
from typing import List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from kivy.uix.image import Image as KivyImage
from kivy.core.image import Image as CoreImage

from data.storage import Transaction


def _fig_to_kivy(fig) -> KivyImage:
    """Convert a matplotlib figure to a Kivy Image widget."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    img = KivyImage()
    img.texture = CoreImage(buf, ext="png").texture
    return img


def donut_chart(income: float, expenses: float) -> KivyImage:
    """Donut chart: income vs expenses."""
    fig, ax = plt.subplots(figsize=(4, 3.2), facecolor="#F7F7F3")
    total = income + expenses

    if total == 0:
        ax.text(0.5, 0.5, "No data yet", ha="center", va="center",
                fontsize=14, color="#999", transform=ax.transAxes)
        ax.axis("off")
    else:
        wedges, _ = ax.pie(
            [income, expenses],
            colors=["#2ECC71", "#F24C3D"],
            startangle=90,
            wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
        )
        labels = [f"Income\n€{income:.0f}", f"Expenses\n€{expenses:.0f}"]
        ax.legend(wedges, labels, loc="lower center", ncol=2,
                  fontsize=9, frameon=False, bbox_to_anchor=(0.5, -0.12))
        balance = income - expenses
        bal_color = "#2ECC71" if balance >= 0 else "#F24C3D"
        ax.text(0, 0.08, "Balance", ha="center", va="center", fontsize=9, color="#999")
        ax.text(0, -0.12, f"€{balance:.2f}", ha="center", va="center",
                fontsize=13, fontweight="bold", color=bal_color)

    ax.set_title("Income vs Expenses", fontsize=12, fontweight="bold",
                 color="#1A1A1A", pad=10)
    plt.tight_layout()
    return _fig_to_kivy(fig)


def bar_chart(transactions: List[Transaction]) -> KivyImage:
    """Bar chart of the last 10 transactions."""
    fig, ax = plt.subplots(figsize=(4, 3), facecolor="#F7F7F3")
    ax.set_facecolor("#F7F7F3")
    last = transactions[-10:]

    if not last:
        ax.text(0.5, 0.5, "No data yet", ha="center", va="center",
                fontsize=14, color="#999", transform=ax.transAxes)
        ax.axis("off")
    else:
        labels  = [t.description[:8] for t in last]
        amounts = [t.amount for t in last]
        colors  = ["#2ECC71" if t.is_income() else "#F24C3D" for t in last]
        x = range(len(last))
        bars = ax.bar(x, amounts, color=colors, edgecolor="white",
                      linewidth=1.5, width=0.6, zorder=3)
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, fontsize=7, rotation=30, ha="right", color="#666")
        ax.yaxis.set_tick_params(labelsize=8, labelcolor="#666")
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        for spine in ["left", "bottom"]:
            ax.spines[spine].set_color("#DDD")
        ax.grid(axis="y", color="#E8E8E4", linewidth=0.8, zorder=0)
        for bar, amt in zip(bars, amounts):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(amounts) * 0.02,
                    f"€{amt:.0f}", ha="center", va="bottom", fontsize=7, color="#555")

    ax.set_title("Last 10 Transactions", fontsize=12, fontweight="bold",
                 color="#1A1A1A", pad=10)
    plt.tight_layout()
    return _fig_to_kivy(fig)
