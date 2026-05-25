from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


# ---------------------------------------------------------------------------
# Coverage and predictor-readiness diagnostics
# ---------------------------------------------------------------------------
#
# At the end of Part 5 we have a single integration-stage master dataset.
# Before handing it to the modelling stage we want to know:
#
#   1.  *Per-source / per-variable coverage*  — what fraction of the
#       master (time x location) grid each predictor actually fills.
#   2.  *Per-station coverage*                — which stations are
#       feature-complete and which are partial.
#   3.  *Predictor readiness*                 — which variables clear a
#       configurable coverage threshold and can be used by the model,
#       and which are too sparse.
#
# These reports are integration-stage diagnostics, not modelling-stage
# choices: a variable below the readiness threshold is *flagged*, not
# silently dropped.


@dataclass
class ReadinessThresholds:
    """Coverage levels separating ready / borderline / not-ready predictors."""
    ready_min: float = 0.85
    borderline_min: float = 0.50


# ---------------------------------------------------------------------------
# Coverage by source x variable
# ---------------------------------------------------------------------------
def coverage_by_source_variable(
    long: pd.DataFrame,
    master: pd.DataFrame,
    *,
    time_col: str = "time",
    location_id_col: str = "location_id",
    value_col: str = "value",
    source_col: str = "source",
    variable_col: str = "variable",
) -> pd.DataFrame:
    """
    Fraction of expected master cells that carry a non-null value, broken
    down per ``(source, variable)``.

    The expected total is ``len(master)`` — the size of the master
    ``(time, location_id)`` skeleton.

    Returns
    -------
    DataFrame with columns
        source, variable, observed, expected, coverage
    sorted by ``coverage`` ascending so the gaps surface first.
    """
    if long.empty or master.empty:
        return pd.DataFrame(columns=[
            source_col, variable_col, "observed", "expected", "coverage",
        ])

    expected = len(master)
    time_varying = long[long[time_col].notna()]

    rows: list[dict] = []
    for (src, var), g in time_varying.groupby(
        [source_col, variable_col], sort=True
    ):
        observed = int(
            g[g[value_col].notna()]
            .drop_duplicates(subset=[time_col, location_id_col])
            .shape[0]
        )
        rows.append({
            source_col: src,
            variable_col: var,
            "observed": observed,
            "expected": expected,
            "coverage": observed / expected if expected else float("nan"),
        })

    return (
        pd.DataFrame(rows)
        .sort_values("coverage", ascending=True)
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# Coverage by station x variable
# ---------------------------------------------------------------------------
def coverage_by_station_variable(
    long: pd.DataFrame,
    master: pd.DataFrame,
    *,
    time_col: str = "time",
    location_id_col: str = "location_id",
    value_col: str = "value",
    variable_col: str = "variable",
) -> pd.DataFrame:
    """
    Fraction of expected hours per ``(location_id, variable)``.

    Returns
    -------
    Wide DataFrame with rows indexed by ``location_id`` and columns
    one per ``variable``.  Cell values are in ``[0, 1]``.
    """
    if long.empty or master.empty:
        return pd.DataFrame()

    expected_per_loc = master.groupby(location_id_col).size()
    time_varying = long[long[time_col].notna()]

    rows: list[dict] = []
    for (loc, var), g in time_varying.groupby(
        [location_id_col, variable_col], sort=True
    ):
        observed = int(
            g[g[value_col].notna()]
            .drop_duplicates(subset=[time_col])
            .shape[0]
        )
        expected = int(expected_per_loc.get(loc, 0))
        rows.append({
            location_id_col: loc,
            variable_col: var,
            "coverage": observed / expected if expected else float("nan"),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.pivot(
        index=location_id_col, columns=variable_col, values="coverage"
    ).round(3)


# ---------------------------------------------------------------------------
# Predictor readiness
# ---------------------------------------------------------------------------
def predictor_readiness(
    long: pd.DataFrame,
    master: pd.DataFrame,
    *,
    thresholds: ReadinessThresholds | None = None,
    time_col: str = "time",
    location_id_col: str = "location_id",
    value_col: str = "value",
    variable_col: str = "variable",
) -> pd.DataFrame:
    """
    Per-variable verdict: ``ready`` / ``borderline`` / ``not_ready``.

    A variable is *ready* when its overall coverage clears
    ``thresholds.ready_min``; *borderline* between that and
    ``borderline_min``; *not_ready* below.

    Returns
    -------
    DataFrame with columns
        variable, coverage, n_stations_full, n_stations_partial,
        n_stations_empty, verdict
    where ``n_stations_full`` is the count of stations whose individual
    coverage on that variable is >= ``ready_min``, and so on.
    """
    thr = thresholds or ReadinessThresholds()

    if long.empty or master.empty:
        return pd.DataFrame(columns=[
            variable_col, "coverage",
            "n_stations_full", "n_stations_partial", "n_stations_empty",
            "verdict",
        ])

    expected_per_loc = master.groupby(location_id_col).size()
    total_expected = len(master)
    time_varying = long[long[time_col].notna()]

    rows: list[dict] = []
    for var, g in time_varying.groupby(variable_col, sort=True):
        observed_total = int(
            g[g[value_col].notna()]
            .drop_duplicates(subset=[time_col, location_id_col])
            .shape[0]
        )
        overall = observed_total / total_expected if total_expected else float("nan")

        per_loc_obs = (
            g[g[value_col].notna()]
            .drop_duplicates(subset=[time_col, location_id_col])
            .groupby(location_id_col)
            .size()
            .reindex(expected_per_loc.index, fill_value=0)
        )
        per_loc_cov = per_loc_obs / expected_per_loc

        n_full = int((per_loc_cov >= thr.ready_min).sum())
        n_part = int(((per_loc_cov >= thr.borderline_min) & (per_loc_cov < thr.ready_min)).sum())
        n_empty = int((per_loc_cov < thr.borderline_min).sum())

        if overall >= thr.ready_min:
            verdict = "ready"
        elif overall >= thr.borderline_min:
            verdict = "borderline"
        else:
            verdict = "not_ready"

        rows.append({
            variable_col: var,
            "coverage": overall,
            "n_stations_full": n_full,
            "n_stations_partial": n_part,
            "n_stations_empty": n_empty,
            "verdict": verdict,
        })

    out = pd.DataFrame(rows).sort_values("coverage", ascending=False).reset_index(drop=True)
    return out


# ---------------------------------------------------------------------------
# One-shot bundle
# ---------------------------------------------------------------------------
def summarize(
    long: pd.DataFrame,
    master: pd.DataFrame,
    *,
    thresholds: ReadinessThresholds | None = None,
) -> dict[str, pd.DataFrame]:
    """
    Run all three reports and return them as a single dict.

    Returns
    -------
    dict with keys
        "by_source_variable", "by_station", "readiness"
    """
    return {
        "by_source_variable": coverage_by_source_variable(long, master),
        "by_station": coverage_by_station_variable(long, master),
        "readiness": predictor_readiness(
            long, master, thresholds=thresholds,
        ),
    }


def print_summary(report: dict[str, pd.DataFrame]) -> None:
    """Pretty-print a bundle from :func:`summarize`."""
    for name in ("by_source_variable", "by_station", "readiness"):
        df = report.get(name)
        print(f"\n=== {name.upper()} ===")
        if df is None or df.empty:
            print("(none)")
            continue
        # Round float columns for readability.
        df_out = df.copy()
        for col in df_out.select_dtypes(include="float").columns:
            df_out[col] = df_out[col].round(3)
        print(df_out.to_string(index=("by_station" in name)))
