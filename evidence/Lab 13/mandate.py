"""Lab 13 mandate checker. Standard library only; weights are percentages."""

# Editable inputs: reserve and distributions are USD millions.
HOLDINGS = {
    "Cash": {"issuer": "none", "days": 0, "reserve_eligible": True},
    "Treasury bills": {"issuer": "U.S. Treasury", "days": 1, "reserve_eligible": True},
    "Treasury 10-year note": {"issuer": "U.S. Treasury", "days": 1, "reserve_eligible": True},
    "Global equity index fund": {"issuer": "diversified fund", "days": 2, "reserve_eligible": False},
    "Investment-grade bond fund": {"issuer": "diversified fund", "days": 3, "reserve_eligible": False},
    "Private real estate fund": {"issuer": "diversified fund", "days": 90, "reserve_eligible": False},
    "Acme Corp bonds": {"issuer": "Acme Corp", "days": 4, "reserve_eligible": False},
    "Acme Corp stock": {"issuer": "Acme Corp", "days": 1, "reserve_eligible": False},
}
# Entries follow the HOLDINGS order above; zero-weight holdings remain explicit.
CANDIDATES = {
    "A": dict(zip(HOLDINGS, [2, 2, 10, 60, 26, 0, 0, 0])),
    "B": dict(zip(HOLDINGS, [1, 0, 0, 55, 20, 15, 5, 4])),
    "C": dict(zip(HOLDINGS, [1, 1, 0, 70, 20, 0, 0, 8])),
    "D": dict(zip(HOLDINGS, [100, 0, 0, 0, 0, 0, 0, 0])),
}
RESERVE_SIZE = 100.0
QUARTERLY_DISTRIBUTION = 0.75
QUARTERS_TO_COVER = 4
LIQUIDITY_WINDOW = 5
MINIMUM_LIQUID_SHARE = 90.0
ISSUER_LIMIT = 8.0
EXEMPT_ISSUERS = {"none", "U.S. Treasury", "diversified fund"}
TOLERANCE = 1e-9


def reserve_minimum():
    return QUARTERS_TO_COVER * QUARTERLY_DISTRIBUTION / RESERVE_SIZE * 100


def evaluate(weights):
    """Return labeled measured values and pass flags, without rounding tests."""
    if set(weights) != set(HOLDINGS):
        raise ValueError("Each candidate must contain exactly the listed holdings.")
    company_weights = {}
    for holding, weight in weights.items():
        issuer = HOLDINGS[holding]["issuer"]
        if issuer not in EXEMPT_ISSUERS:
            company_weights[issuer] = company_weights.get(issuer, 0.0) + weight
    total = sum(weights.values())
    lowest = min(weights.values())
    reserve = sum(w for h, w in weights.items() if HOLDINGS[h]["reserve_eligible"])
    liquid = sum(w for h, w in weights.items() if HOLDINGS[h]["days"] <= LIQUIDITY_WINDOW)
    largest = max(company_weights.values(), default=0.0)
    return [
        ("Weights sum to 100", total, abs(total - 100) <= TOLERANCE),
        ("Long-only (lowest weight)", lowest, lowest >= 0),
        (f"Reserve >= {reserve_minimum():.1f}%", reserve, reserve + TOLERANCE >= reserve_minimum()),
        (f"Redeemable in {LIQUIDITY_WINDOW} days >= {MINIMUM_LIQUID_SHARE:.1f}%", liquid, liquid + TOLERANCE >= MINIMUM_LIQUID_SHARE),
        (f"Largest single company <= {ISSUER_LIMIT:.1f}%", largest, largest <= ISSUER_LIMIT + TOLERANCE),
    ]


def main():
    print(f"Reserve minimum: {reserve_minimum():.1f}% of the portfolio")
    for name, weights in CANDIDATES.items():
        print(f"\nCandidate {name}")
        checks = evaluate(weights)
        for label, value, passed in checks:
            print(f"{label}: {value:.1f} {'pass' if passed else 'FAIL'}")
        print("Calendar-year loss: requires CIO clarification")
        failures = sum(not passed for _, _, passed in checks)
        print("passes every checkable rule" if failures == 0 else f"fails {failures} rule(s)")


if __name__ == "__main__":
    main()
