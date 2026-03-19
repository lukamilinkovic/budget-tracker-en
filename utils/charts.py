"""
utils/charts.py
---------------
Responsibility: rendering charts with matplotlib -> Kivy Image widget.
Theme-aware black & green palette (dark = near-black, light = pale green-white).
"""

from data.storage import Transaction
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image as KivyImage
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import io
from typing import List

import matplotlib
matplotlib.use("Agg")


# ── Palettes ───────────────────────────────────────────────────────────────

_DARK = {
    "bg":           "#080A08",
    "panel":        "#0E110E",
    "grid":         "#1A2A1A",
    "income":       "#1DB954",   # forest green
    "expense":      "#CC3333",   # muted red
    "income_dim":   "#1DB95428",
    "expense_dim":  "#CC333328",
    "text_hi":      "#C8F0C8",   # pale green-white
    "text_lo":      "#3A5A3A",   # dark moss
    "donut_center": "#0E110E",
}

_LIGHT = {
    "bg":           "#EFF5EF",   # pale green-white
    "panel":        "#FFFFFF",
    "grid":         "#DBEBDB",
    "income":       "#118838",   # darker green readable on white
    "expense":      "#B82222",
    "income_dim":   "#11883820",
    "expense_dim":  "#B8222220",
    "text_hi":      "#0A1E0A",   # near-black green
    "text_lo":      "#4A734A",   # mid-green
    "donut_center": "#FFFFFF",
}


def _palette() -> dict:
    from utils.theme import is_dark
    return _DARK if is_dark() else _LIGHT


def _fig_to_kivy(fig) -> KivyImage:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    img = KivyImage()
    img.texture = CoreImage(buf, ext="png").texture
    return img


# ── Donut Chart ────────────────────────────────────────────────────────────

def donut_chart(income: float, expenses: float) -> KivyImage:
    p = _palette()
    fig, ax = plt.subplots(figsize=(4.2, 3.4), facecolor=p["bg"])
    ax.set_facecolor(p["bg"])

    if income == 0 and expenses == 0:
        ring = plt.Circle((0, 0), 0.72, color=p["grid"],  zorder=1)
        circle = plt.Circle((0, 0), 0.52, color=p["panel"], zorder=2)
        ax.add_patch(ring)
        ax.add_patch(circle)
        ax.text(0,  0.07, "NO DATA",           ha="center", va="center",
                fontsize=9,   color=p["text_lo"], fontfamily="monospace",
                fontweight="bold", zorder=3)
        ax.text(0, -0.12, "Add a transaction", ha="center", va="center",
                fontsize=7.5, color=p["text_lo"], zorder=3)
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.axis("off")
    else:
        total = income + expenses
        i_pct = income / total * 100
        e_pct = expenses / total * 100

        wedges, _ = ax.pie(
            [income, expenses],
            colors=[p["income"], p["expense"]],
            startangle=90,
            wedgeprops=dict(width=0.42, edgecolor=p["bg"], linewidth=3),
            counterclock=False,
        )

        centre = plt.Circle((0, 0), 0.49, color=p["donut_center"], zorder=3)
        ax.add_patch(centre)

        balance = income - expenses
        bal_color = p["income"] if balance >= 0 else p["expense"]
        sign = "+" if balance >= 0 else ""

        ax.text(0,  0.14, "BALANCE", ha="center", va="center",
                fontsize=6.5, color=p["text_lo"], fontfamily="monospace",
                fontweight="bold", zorder=4)
        ax.text(0, -0.07, f"{sign}€{balance:,.2f}", ha="center", va="center",
                fontsize=11,  color=bal_color, fontweight="bold", zorder=4)

        legend_elements = [
            mpatches.Patch(facecolor=p["income"],
                           label=f"Income  €{income:,.0f} ({i_pct:.0f}%)"),
            mpatches.Patch(facecolor=p["expense"],
                           label=f"Expense €{expenses:,.0f} ({e_pct:.0f}%)"),
        ]
        ax.legend(
            handles=legend_elements,
            loc="lower center", ncol=2,
            fontsize=7.5, frameon=False,
            bbox_to_anchor=(0.5, -0.18),
            labelcolor=p["text_hi"],
        )

    ax.set_title("INCOME  VS  EXPENSES", fontsize=9, fontweight="bold",
                 color=p["text_lo"], fontfamily="monospace", pad=10, loc="center")
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout(pad=0.6)
    return _fig_to_kivy(fig)


# ── Bar Chart ──────────────────────────────────────────────────────────────

def bar_chart(transactions: List[Transaction]) -> KivyImage:
    p = _palette()
    fig, ax = plt.subplots(figsize=(4.2, 3.0), facecolor=p["bg"])
    ax.set_facecolor(p["panel"])

    last = transactions[-10:]

    if not last:
        ax.text(0.5, 0.5, "NO TRANSACTIONS", ha="center", va="center",
                fontsize=9, color=p["text_lo"], fontfamily="monospace",
                fontweight="bold", transform=ax.transAxes)
        ax.axis("off")
    else:
        labels = [t.description[:9] for t in last]
        amounts = [t.amount for t in last]
        colors = [p["income"] if t.is_income() else p["expense"] for t in last]
        dim_col = [p["income_dim"] if t.is_income() else p["expense_dim"]
                   for t in last]
        x = np.arange(len(last))
        max_val = max(amounts) if amounts else 1

        ax.bar(x, amounts, color=dim_col, width=0.55, zorder=1)
        bars = ax.bar(x, amounts, color=colors, width=0.55, zorder=2,
                      linewidth=0, alpha=0.92)

        cap_h = max_val * 0.018
        for xi, amt, col in zip(x, amounts, colors):
            ax.bar(xi, cap_h, bottom=amt - cap_h, color=col,
                   width=0.55, zorder=3, linewidth=0, alpha=1.0)

        for bar, amt in zip(bars, amounts):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max_val * 0.04,
                f"€{amt:.0f}",
                ha="center", va="bottom",
                fontsize=6.5, color=p["text_hi"], fontfamily="monospace",
            )

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=7, rotation=28, ha="right",
                           color=p["text_lo"], fontfamily="monospace")
        ax.yaxis.set_tick_params(labelsize=7, labelcolor=p["text_lo"])
        ax.set_ylim(0, max_val * 1.25)
        ax.grid(axis="y", color=p["grid"], linewidth=0.7, zorder=0,
                linestyle="--", dashes=(4, 6))

        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        for spine in ["left", "bottom"]:
            ax.spines[spine].set_color(p["grid"])
            ax.spines[spine].set_linewidth(0.8)

    ax.set_title("LAST 10  TRANSACTIONS", fontsize=9, fontweight="bold",
                 color=p["text_lo"], fontfamily="monospace", pad=8, loc="center")

    plt.tight_layout(pad=0.6)
    return _fig_to_kivy(fig)
