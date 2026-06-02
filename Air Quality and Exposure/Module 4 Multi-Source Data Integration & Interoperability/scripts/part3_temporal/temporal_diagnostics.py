from __future__ import annotations

import pandas as pd


# ---------------------------------------------------------------------------
# Diagnostics for the integration stage
# ---------------------------------------------------------------------------
#
# Once every source has been aligned to the master hourly index, you want to
# know:
#
#   1.  *Coverage*      -> what fraction of expected (time, location) cells
#                          actually carry a value, per source?
#   2.  *Missingness*   -> how does coverage vary day by day?
#   3.  *Duplicates*    -> do any (time, location, variable) keys appear
#                          more than once?
#   4.  *Gaps*          -> what are the longest stretches of missing data?
#
# The functions below return small DataFrames suitable for printing in a
# notebook or persisting as integration-stage reports.


# ---------------------------------------------------------------------------
# Coverage
# ---------------------------------------------------------------------------
def coverage_by_source(
    df: pd.DataFrame,
    master: pd.DataFrame,
    *,
    source_col: str = "source",
    time_col: str = "time",
    location_id_col: str = "location_id",
    value_col: str = "value",
) -> pd.DataFrame:
    """
    Fraction of expected master timestamps that carry a non-null value,
    broken down per ``(source, location_id)``.

    Returns
    -------
    DataFrame with columns
        source, location_id, observed, expected, coverage
    where ``coverage`` is in ``[0, 1]``.
    """
    if df.empty:
        return pd.DataFrame(
            columns=[source_col, location_id_col, "observed", "expected", "coverage"]
        )

    expected_per_loc = master.groupby(location_id_col).size()

    rows = []
    for (source, loc), g in df.groupby([source_col, location_id_col], sort=True):
        observed = int(g[g[value_col].notna()][time_col].nunique())
        expected = int(expected_per_loc.get(loc, 0))
        coverage = (observed / expected) if expected else float("nan")
        rows.append(
            {
                source_col: source,
                location_id_col: loc,
                "observed": observed,
                "expected": expected,
                "coverage": coverage,
            }
        )
    return pd.DataFrame(rows).sort_values([source_col, location_id_col]).reset_index(
        drop=True
    )


# ---------------------------------------------------------------------------
# Missingness by day
# ---------------------------------------------------------------------------
def missingness_by_day(
    df: pd.DataFrame,
    master: pd.DataFrame,
    *,
    time_col: str = "time",
    location_id_col: str = "location_id",
    source_col: str = "source",
    value_col: str = "value",
) -> pd.DataFrame:
    """
    Per ``(location_id, date, source)``, fraction of expected hours that have
    a non-null value vs. that are missing.

    Returns
    -------
    DataFrame with columns
        location_id, date, source, expected, present, missingness
    where ``missingness`` is in ``[0, 1]``.
    """
    if df.empty:
        return pd.DataFrame(
            columns=[
                location_id_col, "date", source_col,
                "expected", "present", "missingness",
            ]
        )

    df = df.copy()
    df["date"] = pd.to_datetime(df[time_col]).dt.date

    master = master.copy()
    master["date"] = pd.to_datetime(master[time_col]).dt.date
    expected = master.groupby([location_id_col, "date"]).size()

    rows = []
    for (loc, date, source), g in df.groupby(
        [location_id_col, "date", source_col], sort=True
    ):
        present = int(g[value_col].notna().sum())
        exp = int(expected.get((loc, date), 0))
        miss = 1 - (present / exp) if exp else float("nan")
        rows.append(
            {
                location_id_col: loc,
                "date": date,
                source_col: source,
                "expected": exp,
                "present": present,
                "missingness": miss,
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Duplicates
# ---------------------------------------------------------------------------
def find_duplicates(
    df: pd.DataFrame,
    *,
    time_col: str = "time",
    group_cols: list[str] | None = None,
) -> pd.DataFrame:
    """
    Locate ``(group_cols, time)`` combinations that appear more than once.

    A common cause is the autumn DST "fall-back" hour appearing twice when
    a tz-naive local timestamp is left un-localised.

    Returns
    -------
    DataFrame with the group columns, ``time``, and ``n_rows`` (>= 2),
    sorted by ``n_rows`` descending.
    """
    if group_cols is None:
        group_cols = ["location_id", "source", "variable"]
    cols = group_cols + [time_col]
    counts = df.groupby(cols).size().reset_index(name="n_rows")
    return (
        counts[counts["n_rows"] > 1]
        .sort_values("n_rows", ascending=False)
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# Time gaps
# ---------------------------------------------------------------------------
def time_gap_report(
    df: pd.DataFrame,
    *,
    expected_freq: str = "1h",
    time_col: str = "time",
    group_cols: list[str] | None = None,
    top_n: int = 10,
) -> pd.DataFrame:
    """
    The largest gaps between consecutive observations, per series.

    A "gap" is any interval between two successive timestamps that exceeds
    ``expected_freq``.

    Parameters
    ----------
    expected_freq : str, default ``"1h"``
        The cadence the series is *meant* to have.
    group_cols : list of str
        Columns that identify a series.  Default
        ``["location_id", "source", "variable"]``.
    top_n : int, default 10
        Number of largest gaps to keep.

    Returns
    -------
    DataFrame with the group columns plus ``gap_start``, ``gap_end``,
    ``gap_duration``, sorted by ``gap_duration`` descending.
    """
    if group_cols is None:
        group_cols = ["location_id", "source", "variable"]
    exp = pd.Timedelta(expected_freq)

    rows = []
    for keys, g in df.groupby(group_cols, sort=False):
        g = g.sort_values(time_col)
        if len(g) < 2:
            continue
        times = pd.to_datetime(g[time_col]).reset_index(drop=True)
        deltas = times.diff().iloc[1:]
        gap_mask = deltas > exp
        if not gap_mask.any():
            continue
        if not isinstance(keys, tuple):
            keys = (keys,)
        starts = times.iloc[:-1][gap_mask.values]
        ends = times.iloc[1:][gap_mask.values]
        for start, end, delta in zip(starts, ends, deltas[gap_mask]):
            row = dict(zip(group_cols, keys))
            row["gap_start"] = start
            row["gap_end"] = end
            row["gap_duration"] = delta
            rows.append(row)

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return (
        out.sort_values("gap_duration", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# One-shot bundle
# ---------------------------------------------------------------------------
def summarize(
    df: pd.DataFrame,
    master: pd.DataFrame,
    *,
    expected_freq: str = "1h",
    group_cols: list[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """
    Run all four diagnostics and return them as a single dict.

    Convenient for notebooks and integration-stage reports.

    Returns
    -------
    dict with keys
        "coverage", "missingness", "duplicates", "gaps"
    each mapping to a DataFrame.
    """
    return {
        "coverage": coverage_by_source(df, master),
        "missingness": missingness_by_day(df, master),
        "duplicates": find_duplicates(df, group_cols=group_cols),
        "gaps": time_gap_report(
            df, expected_freq=expected_freq, group_cols=group_cols
        ),
    }


def print_summary(report: dict[str, pd.DataFrame]) -> None:
    """
    Pretty-print a diagnostics bundle in a notebook-friendly way.

    Pass the dict returned by :func:`summarize`.
    """
    for name in ("coverage", "missingness", "duplicates", "gaps"):
        df = report.get(name)
        print(f"\n=== {name.upper()} ===")
        if df is None or df.empty:
            print("(none)")
        else:
            print(df.to_string(index=False))
