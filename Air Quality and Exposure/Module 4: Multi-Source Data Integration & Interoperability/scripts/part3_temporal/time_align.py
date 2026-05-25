from __future__ import annotations

import pandas as pd


# ---------------------------------------------------------------------------
# Conventions used throughout this module
# ---------------------------------------------------------------------------
#
# Time axis        : UTC, hourly, *period-start* labels.
#                    A row stamped 10:00 carries data valid for 10:00 - 10:59
#                    UTC.  This matches CAMS / ERA5 / Copernicus conventions.
#
# Master index     : the Cartesian product of (location_id) x (hourly axis).
#                    Every observation source is *reindexed* onto this skeleton
#                    so downstream code can join everything on
#                    (time, location_id) without worrying about cadence.
#
# Frequency strings: pandas "1h", "10min", "1D", ... .  Lower-case "h" because
#                    upper-case "H" is deprecated since pandas 2.2.


# ---------------------------------------------------------------------------
# 1. Time-zone standardisation
# ---------------------------------------------------------------------------
def standardize_timezone(
    df: pd.DataFrame,
    time_col: str = "time",
    source_tz: str | None = None,
    target_tz: str = "UTC",
    ambiguous: str | bool = "raise",
    nonexistent: str = "raise",
) -> pd.DataFrame:
    """
    Convert a time column to a target time zone (default UTC).

    Three cases are handled:

    1. **Already tz-aware** -> simply converted to ``target_tz``.
    2. **tz-naive and ``source_tz`` is given** -> localised to ``source_tz``
       (handling DST via ``ambiguous`` / ``nonexistent``), then converted to
       ``target_tz``.
    3. **tz-naive and ``source_tz`` is None** -> assumed to be in
       ``target_tz`` already; we just attach the label.

    Parameters
    ----------
    df : DataFrame
    time_col : str
        Name of the column holding timestamps.
    source_tz : str, optional
        IANA name of the source time zone, e.g. ``"Europe/Zagreb"``.
        Required when the column is tz-naive but not in UTC.
    target_tz : str, default ``"UTC"``
        IANA name of the target time zone.
    ambiguous : {"raise", "infer", True, False}
        How to handle the autumn "fall-back" hour (e.g. 02:00 - 03:00 on the
        last Sunday of October in Europe, which happens twice).  Default
        ``"raise"`` forces the caller to be explicit.
    nonexistent : {"raise", "shift_forward", "shift_backward", "NaT"}
        How to handle the spring "spring-forward" hour that does not exist
        in local time.  Default ``"raise"``.

    Returns
    -------
    DataFrame with ``time_col`` replaced by a tz-aware datetime64 column.
    """
    out = df.copy()
    s = pd.to_datetime(out[time_col], errors="coerce")

    if s.dt.tz is None:
        if source_tz is None:
            s = s.dt.tz_localize(target_tz)
        else:
            s = s.dt.tz_localize(
                source_tz, ambiguous=ambiguous, nonexistent=nonexistent
            )
            s = s.dt.tz_convert(target_tz)
    else:
        s = s.dt.tz_convert(target_tz)

    out[time_col] = s
    return out


# ---------------------------------------------------------------------------
# 2. Resampling to hourly (or any target frequency)
# ---------------------------------------------------------------------------
def resample_to_hourly(
    df: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str = "value",
    group_cols: list[str] | None = None,
    agg: str | dict = "mean",
    label: str = "left",
    closed: str = "left",
    freq: str = "1h",
) -> pd.DataFrame:
    """
    Resample sub-hourly observations to an hourly (or other) cadence with
    explicit averaging conventions.

    Parameters
    ----------
    df : DataFrame
        Long-format data (one row per measurement).
    time_col : str
    value_col : str
    group_cols : list of str, optional
        Columns that identify an independent series (typically
        ``["location_id", "source", "variable"]``).  Resampling is done
        per group.
    agg : str or dict, default ``"mean"``
        Aggregation function used over each hour.  Use ``"sum"`` for
        accumulations (e.g. precipitation), ``"max"`` for peaks
        (e.g. NO2 peaks), ``"mean"`` for concentrations.
    label : {"left", "right"}, default ``"left"``
        Which end of the period is used as the timestamp label.
        ``"left"`` -> 10:00 stands for the average over 10:00 - 10:59.
    closed : {"left", "right"}, default ``"left"``
        Which side of the period is inclusive.  Keep it consistent with
        ``label``.
    freq : str, default ``"1h"``
        Resampling frequency.  Pass ``"1D"`` to aggregate to daily.

    Returns
    -------
    DataFrame in the same shape as the input, with ``time_col`` replaced by
    period-start timestamps and ``value_col`` by the aggregated values.
    """
    if group_cols is None:
        group_cols = []

    out = df.copy()
    out[time_col] = pd.to_datetime(out[time_col])

    def _resample_one(g: pd.DataFrame) -> pd.DataFrame:
        return (
            g.set_index(time_col)[value_col]
            .resample(freq, label=label, closed=closed)
            .agg(agg)
            .to_frame(value_col)
            .reset_index()
        )

    if not group_cols:
        return _resample_one(out)

    pieces: list[pd.DataFrame] = []
    for keys, g in out.groupby(group_cols, sort=False):
        resamp = _resample_one(g)
        if not isinstance(keys, tuple):
            keys = (keys,)
        for col, val in zip(group_cols, keys):
            resamp[col] = val
        pieces.append(resamp)

    if not pieces:
        return out.iloc[0:0][[time_col] + group_cols + [value_col]]

    cols = [time_col] + group_cols + [value_col]
    return pd.concat(pieces, ignore_index=True)[cols]


# ---------------------------------------------------------------------------
# 3. Master hourly index
# ---------------------------------------------------------------------------
def build_master_index(
    start: str | pd.Timestamp,
    end: str | pd.Timestamp,
    locations: pd.DataFrame,
    *,
    freq: str = "1h",
    tz: str = "UTC",
    location_id_col: str = "location_id",
) -> pd.DataFrame:
    """
    Build a complete ``(time, location_id)`` skeleton at the given frequency.

    Every location appears at every timestamp in ``[start, end]``.  Any
    extra columns on ``locations`` (``lat``, ``lon``, ``station_name``,
    ``country``) are carried through verbatim, so downstream joins do not
    have to look them up again.

    Parameters
    ----------
    start, end : datetime-like
        Bounds of the master axis.  Both inclusive.  If ``tz`` is set, these
        are interpreted in that time zone.
    locations : DataFrame
        Must contain ``location_id_col``.  Other columns are carried along.
    freq : str, default ``"1h"``
    tz : str, default ``"UTC"``

    Returns
    -------
    DataFrame with at least ``["time", "location_id"]`` (plus any extra
    location columns), sorted by ``(time, location_id)``.
    """
    time_axis = pd.date_range(start=start, end=end, freq=freq, tz=tz)

    extra_cols = [
        c for c in ("lat", "lon", "station_name", "country")
        if c in locations.columns
    ]
    locs = locations[[location_id_col] + extra_cols].drop_duplicates(
        subset=[location_id_col]
    )

    grid = locs.merge(pd.DataFrame({"time": time_axis}), how="cross")
    return (
        grid[["time", location_id_col] + extra_cols]
        .sort_values(["time", location_id_col])
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# 4. Aligning source tables onto the master index
# ---------------------------------------------------------------------------
def align_to_master_index(
    df: pd.DataFrame,
    master: pd.DataFrame,
    *,
    time_col: str = "time",
    location_id_col: str = "location_id",
    tolerance: str | pd.Timedelta | None = None,
    method: str = "nearest",
) -> pd.DataFrame:
    """
    Snap a source table onto the master hourly axis.

    For each ``location_id`` independently we either:

    - **method="exact"** -> inner-join on the exact timestamp; rows whose
      ``time`` does not match any master timestamp are dropped.
    - **method="nearest"** -> per-location ``merge_asof`` finding the
      closest master timestamp within ``tolerance``.

    Parameters
    ----------
    df : DataFrame
        Long-format source table.  Must contain ``time_col`` and
        ``location_id_col``.
    master : DataFrame
        Output of :func:`build_master_index`.
    tolerance : str or Timedelta, optional
        Maximum admissible gap when ``method="nearest"``.  Rows beyond
        ``tolerance`` are dropped.  ``None`` disables the limit.
    method : {"nearest", "exact"}

    Returns
    -------
    DataFrame with the same columns as ``df``, ``time_col`` replaced by the
    snapped master timestamp.  Rows that could not be aligned are dropped.
    """
    if method not in ("nearest", "exact"):
        raise ValueError(f"Unknown alignment method: {method!r}")

    if df.empty:
        return df.copy()

    tol = (
        pd.Timedelta(tolerance)
        if tolerance is not None and not isinstance(tolerance, pd.Timedelta)
        else tolerance
    )

    pieces: list[pd.DataFrame] = []
    for loc, g in df.groupby(location_id_col, sort=False):
        m = master[master[location_id_col] == loc][[time_col]].sort_values(time_col)
        if m.empty:
            continue
        g_sorted = g.sort_values(time_col).copy()

        if method == "exact":
            piece = g_sorted.merge(m, on=time_col, how="inner")
        else:
            piece = pd.merge_asof(
                g_sorted,
                m.rename(columns={time_col: "_aligned_time"}),
                left_on=time_col,
                right_on="_aligned_time",
                direction="nearest",
                tolerance=tol,
            )
            piece = piece.dropna(subset=["_aligned_time"]).copy()
            piece[time_col] = piece["_aligned_time"]
            piece = piece.drop(columns=["_aligned_time"])

        pieces.append(piece)

    if not pieces:
        return df.iloc[0:0].copy()
    return pd.concat(pieces, ignore_index=True)


# ---------------------------------------------------------------------------
# 5. Convenience: fold a long table down to one row per (time, location)
# ---------------------------------------------------------------------------
def to_wide(
    df: pd.DataFrame,
    *,
    time_col: str = "time",
    location_id_col: str = "location_id",
    variable_col: str = "variable",
    value_col: str = "value",
    extra_index_cols: list[str] | None = None,
    agg: str = "first",
) -> pd.DataFrame:
    """
    Pivot a canonical long-format table to one column per variable.

    Useful as the last step before feeding a model: every row is one
    ``(time, location_id)``, every column is one feature.
    """
    if extra_index_cols is None:
        extra_index_cols = [
            c for c in ("lat", "lon") if c in df.columns
        ]
    wide = df.pivot_table(
        index=[time_col, location_id_col] + extra_index_cols,
        columns=variable_col,
        values=value_col,
        aggfunc=agg,
    ).reset_index()
    wide.columns.name = None
    return wide
