"""
analysis/short_report.py

Generate <=8 short report lines from computed fields. No LLM free text.
"""

from typing import List, Dict, Any


def build_short_report(result: Dict[str, Any], lat: float, lon: float) -> List[str]:
    """Generate <=8 short report lines from computed fields."""
    arms = result["arms_mSv_yr"]
    total = result["total_terrestrial_mSv_yr"]
    risk = result["risk"]["tier"]
    dom = max(arms, key=arms.get)
    share = arms[dom] / total * 100 if total > 0 else 0

    lines = []
    lines.append(f"{dom.capitalize()} is {share:.0f}% of total dose ({arms[dom]:.2f} mSv/yr).")
    lines.append(f"Total terrestrial dose: {total:.2f} mSv/yr — {risk}.")

    # Top factors
    for f in result["factors"][:3]:
        arrow = "↑" if f["direction"] == "up" else "↓" if f["direction"] == "down" else "→"
        lines.append(f"{f['id'].capitalize()}: {f['value']} ({arrow} {f['effect']}).")

    # Comparison
    ratio = total / 2.2
    lines.append(f"{ratio:.1f}× UNSCEAR world average (2.2 mSv/yr).")

    # Confidence
    conf = result["confidence"]
    lines.append(f"Confidence: {conf['level']}. {conf['reason']}.")

    # Resolution
    lines.append(f"Cell: {result['cell_m']} m. Activities: Ra={result['activities']['A_Ra226']:.0f}, Th={result['activities']['A_Th232']:.0f}, K={result['activities']['A_K40']:.0f} Bq/kg.")

    return lines[:8]
