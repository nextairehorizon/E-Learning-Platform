from __future__ import annotations

from typing import Sequence

import pandas as pd


# ---------------------------------------------------------------------------
# Joining canonical long tables onto a single master table
# ---------------------------------------------------------------------------
#
# By the time we reach Part 5 we have several canonical long-format files,
# all sharing the schema:
#
#   time, location_id, lat, lon, variable, value, source, method [,
#   dataset_version]
#
# The job of this module is to stack them into a single integration-stage
# master table without leaking modelling decisions (lags, normalisation,
# train/test splits) into the join itself.
#
# The output keeps two complementary views:
#
#   1.  A *long* master table          — one row per (time, location, var).
#   2.  A *wide*, "model-ready" table  — one row per (time, location),
#                                         one column per variable, plus
#                                         the per-station static context.
#
# The wide table is sorted by ``(location_id, time)`` so that adding lag
# features downstream is a single ``groupby(location_id).shift(k)``.


CANONICAL_COLUMNS = [
    "time", "location_id", "lat", "lon", "variable", "value", "source", "method",
]


# ---------------------------------------------------------------------------
# Stack many long-format sources
# ---------------------------------------------------------------------------
def stack_sources(
    *frames: pd.DataFrame,
    keep_version: bool = True,
) -> pd.DataFrame:
    """
    Concatenate any number of canonical long-format DataFrames.

    Inputs are deduplicated on
    ``(time, location_id, variable, source, method)``; the **first**
    occurrence wins, so order frames most-trusted-first.

    Parameters
    ----------
    *frames : DataFrame
        Each must have the canonical columns.  ``dataset_version`` is
        carried through if every frame has it; otherwise dropped.
    keep_version : bool, default True
        If False, ``dataset_version`` is dropped from the output even
        when present in every input.

    Returns
    -------
    DataFrame with the canonical columns (+ ``dataset_version`` when
    available), sorted by ``(time, location_id, variable, source)``.
    """
    valid = [f for f in frames if f is not None and not f.empty]
    if not valid:
        cols = CANONICAL_COLUMNS + (["dataset_version"] if keep_version else [])
        return pd.DataFrame(columns=cols)

    has_version = keep_version and all("dataset_version" in f.columns for f in valid)

    aligned: list[pd.DataFrame] = []
    target_cols = CANONICAL_COLUMNS + (["dataset_version"] if has_version else [])
    for f in valid:
        g = f.copy()
        for c in target_cols:
            if c not in g.columns:
                g[c] = pd.NA
        aligned.append(g[target_cols])

    out = pd.concat(aligned, ignore_index=True)

    out = out.drop_duplicates(
        subset=["time", "location_id", "variable", "source", "method"],
        keep="first",
    )

    return out.sort_values(
        ["time", "location_id", "variable", "source"]
    ).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Pivot to wide "model-ready" shape
# ---------------------------------------------------------------------------
def to_model_ready(
    long: pd.DataFrame,
    static: pd.DataFrame | None = None,
    *,
    time_col: str = "time",
    location_id_col: str = "location_id",
    variable_col: str = "variable",
    value_col: str = "value",
    extra_index_cols: Sequence[str] = ("lat", "lon"),
    static_value_col: str = "value",
    static_variable_col: str = "variable",
) -> pd.DataFrame:
    """
    Pivot the long master table into model-ready wide form.

    One row per ``(time, location_id)``.  One column per variable.
    Static per-station features are attached on ``location_id`` so they
    repeat across every timestamp at that station.

    The output is sorted by ``(location_id, time)`` so that lag features
    can be added downstream with a single
    ``groupby(location_id).shift(k)`` — *the integration stage prepares
    the structure; it does not pick the lag*.

    Parameters
    ----------
    long : DataFrame
        Time-varying canonical long table (output of :func:`stack_sources`).
    static : DataFrame, optional
        Long-format static-context table (one row per
        ``(location_id, variable)`` with ``time=NaT``).  Pivoted and
        joined on ``location_id``.
    """
    time_varying = long[long[time_col].notna()].copy()

    wide = time_varying.pivot_table(
        index=[time_col, location_id_col] + list(extra_index_cols),
        columns=variable_col,
        values=value_col,
        aggfunc="first",
    ).reset_index()
    wide.columns.name = None

    if static is not None and not static.empty:
        static_wide = static.pivot_table(
            index=[location_id_col],
            columns=static_variable_col,
            values=static_value_col,
            aggfunc="first",
        ).reset_index()
        static_wide.columns.name = None
        wide = wide.merge(static_wide, on=location_id_col, how="left")

    return wide.sort_values([location_id_col, time_col]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Optional lag helper (kept here so the wide table can be enriched
# downstream without re-implementing it; not called by the integration
# stage itself).
# ---------------------------------------------------------------------------
def add_lag_features(
    wide: pd.DataFrame,
    columns: Sequence[str],
    *,
    lags_hours: Sequence[int] = (1, 3, 6, 24),
    time_col: str = "time",
    location_id_col: str = "location_id",
) -> pd.DataFrame:
    """
    Add lagged copies of the named columns.

    Lags are computed per ``location_id`` after sorting by ``time``.
    Useful when the modelling stage opts into using past values of a
    predictor (e.g. PM₂.₅(t-1)).  Each new column is named
    ``<orig>_lag<H>h``.

    Parameters
    ----------
    wide : DataFrame
        Output of :func:`to_model_ready`.
    columns : sequence of str
        Names of columns to lag.  Missing names are skipped silently.
    lags_hours : sequence of int, default ``(1, 3, 6, 24)``
        Lags to add, in **hours**.  Assumes the wide table is hourly.
    """
    out = wide.sort_values([location_id_col, time_col]).copy()
    present = [c for c in columns if c in out.columns]
    grouped = out.groupby(location_id_col, sort=False)

    for col in present:
        for lag in lags_hours:
            out[f"{col}_lag{lag}h"] = grouped[col].shift(lag)

    return out
