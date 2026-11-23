"""Compare three portfolio baselines using decimal returns and volatilities."""

import math


# EDITABLE INPUTS: enter percentages as decimals (3.5% = 0.035).
SLEEVES = [
    {"name": "Treasury bills", "return": 0.035, "volatility": 0.005,
     "reserve_eligible": True},
    {"name": "Treasury 10-year note", "return": 0.043, "volatility": 0.070,
     "reserve_eligible": True},
    {"name": "Investment-grade bond fund", "return": 0.050, "volatility": 0.060,
     "reserve_eligible": False},
    {"name": "Global equity index fund", "return": 0.080, "volatility": 0.160,
     "reserve_eligible": False},
]
# Rows and columns follow the SLEEVES order above.
CORRELATIONS = [
    [1.00, 0.10, 0.05, 0.00],
    [0.10, 1.00, 0.80, -0.10],
    [0.05, 0.80, 1.00, 0.25],
    [0.00, -0.10, 0.25, 1.00],
]
CPI_ESTIMATE = 0.025  # Labelled estimate, not observed CPI.
REAL_RETURN_TARGET = 0.040
OBJECTIVE_RETURN = CPI_ESTIMATE + REAL_RETURN_TARGET
BENCHMARK_ALLOCATIONS = {
    "Investment-grade bond fund": 0.40,
    "Global equity index fund": 0.60,
}


def validate_inputs(sleeves, correlations):
    """Reject invalid inputs before calculating any portfolio."""
    n = len(sleeves)
    if not n or len(correlations) != n or any(len(row) != n for row in correlations):
        raise ValueError("Correlation table must be square and match the sleeves.")
    for i, row in enumerate(correlations):
        for j, value in enumerate(row):
            if not math.isfinite(value) or not -1 <= value <= 1:
                raise ValueError(
                    f"Correlation at row {i + 1}, column {j + 1} must be between -1 and 1."
                )
            if value != correlations[j][i]:
                raise ValueError(
                    f"Correlation table is not symmetric at row {i + 1}, column {j + 1}."
                )
        if row[i] != 1:
            raise ValueError("Every diagonal correlation must equal 1.")
    for sleeve in sleeves:
        if not math.isfinite(sleeve["return"]):
            raise ValueError("Expected returns must be finite.")
        if not math.isfinite(sleeve["volatility"]) or sleeve["volatility"] <= 0:
            raise ValueError("Volatilities must be finite and greater than zero.")
    if len({s["name"] for s in sleeves}) != n:
        raise ValueError("Sleeve names must be unique.")


def covariance_matrix(sleeves, correlations):
    """Compute covariance[i][j] = correlation[i][j] * vol[i] * vol[j]."""
    validate_inputs(sleeves, correlations)
    return [
        [correlations[i][j] * left["volatility"] * right["volatility"]
         for j, right in enumerate(sleeves)]
        for i, left in enumerate(sleeves)
    ]


def benchmark_weights(sleeves, allocations):
    """Map named benchmark allocations to the sleeve order."""
    if set(allocations) - {s["name"] for s in sleeves}:
        raise ValueError("Benchmark allocation refers to an unknown sleeve.")
    weights = [allocations.get(s["name"], 0.0) for s in sleeves]
    if any(w < 0 for w in weights) or not math.isclose(sum(weights), 1.0):
        raise ValueError("Benchmark weights must be nonnegative and sum to 100%.")
    return weights


def equal_weights(sleeves):
    return [1.0 / len(sleeves)] * len(sleeves)


def inverse_volatility_weights(sleeves):
    inverse_vols = [1.0 / s["volatility"] for s in sleeves]
    total = sum(inverse_vols)
    return [value / total for value in inverse_vols]


def expected_return(weights, sleeves):
    return sum(w * s["return"] for w, s in zip(weights, sleeves))


def portfolio_volatility(weights, covariance):
    variance = sum(
        weights[i] * weights[j] * covariance[i][j]
        for i in range(len(weights)) for j in range(len(weights))
    )
    if variance < -1e-12:
        raise ValueError("Correlation inputs produce a negative portfolio variance.")
    return math.sqrt(max(0.0, variance))


def reserve_eligible_weight(weights, sleeves):
    return sum(w for w, s in zip(weights, sleeves) if s["reserve_eligible"])


def meets_objective(portfolio_return, objective):
    return portfolio_return >= objective


def print_portfolio(name, weights, sleeves, covariance, objective):
    result_return = expected_return(weights, sleeves)
    print(f"\n{name}")
    for sleeve, weight in zip(sleeves, weights):
        print(f"  {sleeve['name']}: {weight:.1%}")
    print(f"  Expected return: {result_return:.2%}")
    print(f"  Volatility: {portfolio_volatility(weights, covariance):.2%}")
    print(f"  Reserve-eligible weight: {reserve_eligible_weight(weights, sleeves):.1%}")
    print(f"  Meets objective: {'Yes' if meets_objective(result_return, objective) else 'No'}")


def search_portfolio(sleeves, correlations, objective=OBJECTIVE_RETURN, reserve_minimum=0.03):
    """Exhaust every fully invested long-only mix in 5 percentage point steps."""
    import numpy as np

    if not math.isfinite(objective) or not 0 <= reserve_minimum <= 1:
        raise ValueError("Objective must be finite; reserve minimum must be between 0 and 1.")
    covariance = np.asarray(covariance_matrix(sleeves, correlations))

    def compositions(remaining, count, prefix=()):
        if count == 1:
            yield prefix + (remaining,)
        else:
            for value in range(remaining + 1):
                yield from compositions(remaining - value, count - 1, prefix + (value,))

    weights = np.asarray(list(compositions(20, len(sleeves))), dtype=float) / 20
    returns = weights @ np.asarray([s['return'] for s in sleeves])
    reserves = weights @ np.asarray([s['reserve_eligible'] for s in sleeves], dtype=float)
    feasible = (returns >= objective - 1e-12) & (reserves >= reserve_minimum - 1e-12)
    if not feasible.any():
        return None
    candidates = weights[feasible]
    variances = np.einsum('ij,jk,ik->i', candidates, covariance, candidates)
    best = candidates[int(np.argmin(variances))].tolist()
    return {'weights': best, 'return': expected_return(best, sleeves),
            'volatility': portfolio_volatility(best, covariance),
            'reserve_weight': reserve_eligible_weight(best, sleeves)}


def estimate_from_csv(source, last_36=False):
    """Historical arithmetic mean x 12; sample volatility x sqrt(12).

    Use aligned monthly returns without filling missing prices. The window is
    selected AFTER computing returns, so 36 returns require 37 prices.
    """
    import numpy as np
    import pandas as pd

    frame = pd.read_csv(source)
    if not 4 <= len(frame.columns) <= 7 or frame.columns.duplicated().any():
        raise ValueError('CSV requires a date column and 3 to 6 unique ticker columns.')
    dates = pd.to_datetime(frame.iloc[:, 0], errors='raise')
    months = dates.dt.to_period('M')
    if dates.isna().any() or not dates.is_monotonic_increasing or months.duplicated().any():
        raise ValueError('Dates must be unique months, oldest first.')
    if len(months) < 3 or not np.all(np.diff(months.astype('int64')) == 1):
        raise ValueError('Prices must contain consecutive months, with at least three rows.')
    prices = frame.iloc[:, 1:].apply(pd.to_numeric, errors='raise')
    if not np.isfinite(prices.to_numpy()).all() or (prices <= 0).any().any():
        raise ValueError('All prices must be finite, positive, and present for every ticker.')
    returns = prices.pct_change(fill_method=None).iloc[1:]
    if last_36:
        if len(returns) < 36:
            raise ValueError('Last 36 months requires at least 37 monthly price rows.')
        returns = returns.tail(36)
    means, vols = returns.mean() * 12, returns.std(ddof=1) * math.sqrt(12)
    correlations = returns.corr().to_numpy()
    if not np.isfinite(correlations).all():
        raise ValueError('Cannot estimate correlations for a constant-return asset.')
    sleeves = [{'name': ticker, 'return': float(means[ticker]),
                'volatility': float(vols[ticker]), 'reserve_eligible': False}
               for ticker in prices.columns]
    matrix = correlations.tolist()
    validate_inputs(sleeves, matrix)
    return sleeves, matrix


def main():
    try:
        covariance = covariance_matrix(SLEEVES, CORRELATIONS)
        portfolios = [
            ("Benchmark", benchmark_weights(SLEEVES, BENCHMARK_ALLOCATIONS)),
            ("Equal weight", equal_weights(SLEEVES)),
            ("Inverse volatility", inverse_volatility_weights(SLEEVES)),
        ]
        print(f"Objective: {OBJECTIVE_RETURN:.2%} "
              f"(CPI estimate {CPI_ESTIMATE:.2%} + {REAL_RETURN_TARGET:.2%})")
        for name, weights in portfolios:
            print_portfolio(name, weights, SLEEVES, covariance, OBJECTIVE_RETURN)
    except ValueError as error:
        raise SystemExit(f"Cannot run portfolio analysis: {error}") from None


if __name__ == "__main__":
    main()
