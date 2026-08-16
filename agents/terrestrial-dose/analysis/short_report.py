"""Templated ≤8-line report. No LLM free text."""


def build_short_report(result, lat, lon):
    arms = result["arms_mSv_yr"]
    total = result["total_terrestrial_mSv_yr"]
    risk = result["risk"]["tier"]
    dom = max(arms, key=arms.get)
    share = arms[dom] / total * 100 if total > 0 else 0
    lines = []
    lines.append(f"{dom.capitalize()} is {share:.0f}% of total dose ({arms[dom]:.2f} mSv/yr).")
    lines.append(f"Total terrestrial dose: {total:.2f} mSv/yr — {risk}.")
    for f in result["factors"][:4]:
        a = {"up": "↑", "down": "↓", "neutral": "→", "varies": "↔"}[f["direction"]]
        lines.append(f"{f['id'].capitalize()}: {f['value']} ({a} {f['effect']}).")
    lines.append(f"{total / 2.2:.1f}x UNSCEAR world average (2.2 mSv/yr).")
    lines.append(f"Confidence: {result['confidence']['level']}. {result['confidence']['reason']}.")
    lines.append(
        f"Cell: {result['cell_m']}m. Ra={result['activities']['A_Ra226']:.0f}, "
        f"Th={result['activities']['A_Th232']:.0f}, K={result['activities']['A_K40']:.0f} Bq/kg."
    )
    return lines[:8]
