from __future__ import annotations

import numpy as np
import pandas as pd
import xarray as xr


# A reanalysis file can name its coordinates in many ways.  The first match
# wins, so put the most likely names first.
LAT_CANDIDATES = ["latitude", "lat", "LAT", "Latitude"]
LON_CANDIDATES = ["longitude", "lon", "LON", "Longitude"]
TIME_CANDIDATES = ["time", "valid_time", "forecast_reference_time"]


def load_stations(csv_path: str) -> pd.DataFrame:
    """
    Load a CSV of monitoring stations.

    Required columns:
        location_id   -> unique identifier (text or number)
        lat           -> latitude in decimal degrees
        lon           -> longitude in decimal degrees

    Returns
    -------
    pandas.DataFrame with at least (location_id, lat, lon).
    """
    df = pd.read_csv(csv_path)
    required = {"location_id", "lat", "lon"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Stations file is missing required columns: {missing}. "
            f"Found columns: {list(df.columns)}"
        )

    df = df.dropna(subset=["lat", "lon"]).copy()
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    return df.dropna(subset=["lat", "lon"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Coordinate / variable plumbing
# ---------------------------------------------------------------------------
def _find_coord(ds: xr.Dataset, candidates: list[str], role: str) -> str:
    for n in candidates:
        if n in ds.coords or n in ds.dims:
            return n
    raise ValueError(
        f"Could not find a {role} coordinate in the dataset.  "
        f"Tried {candidates}; available coords: {list(ds.coords)}"
    )


def _find_lat_lon(ds: xr.Dataset) -> tuple[str, str]:
    return (
        _find_coord(ds, LAT_CANDIDATES, "latitude"),
        _find_coord(ds, LON_CANDIDATES, "longitude"),
    )


def _select_variable(
    ds: xr.Dataset, variable: str, level: int | float | None = None
) -> xr.DataArray:
    """
    Pull a single variable out of the dataset and reduce it to (time, lat, lon).

    Reanalysis files often have a vertical 'level' dimension.  If only one
    level is present, we squeeze it transparently.  If several levels are
    present, the caller must specify which one via ``level=``.
    """
    if variable not in ds.data_vars:
        raise KeyError(
            f"Variable '{variable}' not found in dataset.  "
            f"Available: {list(ds.data_vars)}"
        )

    da = ds[variable]

    if "level" in da.dims:
        if da.sizes["level"] == 1:
            da = da.isel(level=0).drop_vars("level", errors="ignore")
        elif level is None:
            raise ValueError(
                f"Variable '{variable}' has multiple vertical levels "
                f"({da.sizes['level']}). Pass level=<value> to choose one. "
                f"Available levels: {da['level'].values.tolist()}"
            )
        else:
            da = da.sel(level=level, method="nearest").drop_vars(
                "level", errors="ignore"
            )

    return da


# ---------------------------------------------------------------------------
# Extraction methods: nearest and bilinear
# ---------------------------------------------------------------------------
def extract_nearest(
    ds: xr.Dataset,
    variables: str | list[str],
    stations: pd.DataFrame,
    *,
    level: int | float | None = None,
    source: str | None = None,
    dataset_version: str | None = None,
) -> pd.DataFrame:
    """
    For each station, take the reanalysis value of the nearest grid cell.

    Parameters
    ----------
    ds : xarray.Dataset
        Opened reanalysis dataset.
    variables : str or list of str
        Variable name(s) to extract.  A list returns one row per
        (time, station, variable).
    stations : DataFrame
        Output of ``load_stations``.
    level : int or float, optional
        Vertical level to select (only needed if the variable has > 1 level).
    source : str, optional
        Override the dataset source label written into the output.
    dataset_version : str, optional
        Override the provenance string written into the output.

    Returns
    -------
    DataFrame with columns:
        time, location_id, lat, lon, variable, value, source, method,
        dataset_version
    """
    return _extract(
        ds=ds,
        variables=variables,
        stations=stations,
        method="nearest",
        level=level,
        source=source,
        dataset_version=dataset_version,
    )


def extract_bilinear(
    ds: xr.Dataset,
    variables: str | list[str],
    stations: pd.DataFrame,
    *,
    level: int | float | None = None,
    source: str | None = None,
    dataset_version: str | None = None,
) -> pd.DataFrame:
    """
    For each station, bilinearly interpolate between the four surrounding
    grid cells.

    Good for continuous, smooth meteorological fields (temperature, wind,
    pressure).  Avoid for accumulated or categorical fields where
    interpolation can introduce nonsense values.
    """
    return _extract(
        ds=ds,
        variables=variables,
        stations=stations,
        method="bilinear",
        level=level,
        source=source,
        dataset_version=dataset_version,
    )


def _extract(
    *,
    ds: xr.Dataset,
    variables: str | list[str],
    stations: pd.DataFrame,
    method: str,
    level: int | float | None,
    source: str | None,
    dataset_version: str | None,
) -> pd.DataFrame:
    if isinstance(variables, str):
        variables = [variables]

    lat_name, lon_name = _find_lat_lon(ds)
    station_lats = xr.DataArray(stations["lat"].values, dims="station")
    station_lons = xr.DataArray(stations["lon"].values, dims="station")

    auto_source = source or ds.attrs.get("source") or ds.attrs.get(
        "title", "reanalysis"
    )
    auto_version = dataset_version or _infer_version(ds)

    frames: list[pd.DataFrame] = []
    for var in variables:
        da = _select_variable(ds, var, level=level)

        if method == "nearest":
            picked = da.sel(
                {lat_name: station_lats, lon_name: station_lons},
                method="nearest",
            )
        elif method == "bilinear":
            # interp needs monotonic coords; sort once before interpolating.
            da_sorted = da.sortby([lat_name, lon_name])
            picked = da_sorted.interp(
                {lat_name: station_lats, lon_name: station_lons}
            )
        else:
            raise ValueError(f"Unknown extraction method: {method!r}")

        frames.append(
            _to_long(
                picked=picked,
                stations=stations,
                variable=var,
                source=auto_source,
                method=method,
                dataset_version=auto_version,
            )
        )

    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# Long-format conversion
# ---------------------------------------------------------------------------
def _to_long(
    picked: xr.DataArray,
    stations: pd.DataFrame,
    variable: str,
    source: str,
    method: str,
    dataset_version: str,
) -> pd.DataFrame:
    picked = picked.squeeze(drop=True)

    # Normalise the time dimension name to "time".
    for cand in ("valid_time", "forecast_reference_time"):
        if cand in picked.dims:
            picked = picked.rename({cand: "time"})

    if "time" not in picked.dims:
        picked = picked.expand_dims("time")

    # Drop the grid lat/lon coords carried along on the station dim so they
    # don't collide with the station's own lat/lon during the merge below.
    picked = picked.reset_coords(drop=True)

    df = picked.to_dataframe(name="value").reset_index()

    stations_indexed = stations.reset_index().rename(columns={"index": "station"})
    df = df.merge(
        stations_indexed[["station", "location_id", "lat", "lon"]],
        on="station",
    )

    df["variable"] = variable
    df["source"] = source
    df["method"] = method
    df["dataset_version"] = dataset_version
    df["time"] = pd.to_datetime(df["time"], errors="coerce")

    return df[
        [
            "time",
            "location_id",
            "lat",
            "lon",
            "variable",
            "value",
            "source",
            "method",
            "dataset_version",
        ]
    ]


def _infer_version(ds: xr.Dataset) -> str:
    """Build a short, human-readable provenance string from the dataset attrs."""
    parts = []
    for key in ("source", "history", "Conventions"):
        v = ds.attrs.get(key)
        if v:
            parts.append(f"{key}={str(v)[:80]}")
    return " | ".join(parts) if parts else "unknown"


# ---------------------------------------------------------------------------
# Time alignment
# ---------------------------------------------------------------------------
def align_to_reference(
    df: pd.DataFrame,
    reference_times,
    *,
    tolerance: str | pd.Timedelta | None = "3h",
    method: str = "nearest",
) -> pd.DataFrame:
    """
    Snap a reanalysis long-format DataFrame onto a reference set of timestamps.

    Use this to bring a dense (e.g. hourly ERA5) feature table onto a sparser
    grid (e.g. 6-hourly CAMS analysis or ground-station sampling times) so the
    two can be joined on (time, location_id).

    Parameters
    ----------
    df : DataFrame
        Long-format reanalysis output (must have a ``time`` column).
    reference_times : iterable of datetime-like
        The timestamps you want the output to land on.
    tolerance : str or Timedelta, optional
        Maximum time gap allowed when snapping.  Rows that have no reference
        timestamp within ``tolerance`` are dropped.  Pass None to disable.
    method : {"nearest", "exact"}
        ``nearest`` snaps each row to the closest reference timestamp.
        ``exact`` keeps only rows whose ``time`` already matches a reference
        timestamp.

    Returns
    -------
    DataFrame with the same columns, ``time`` replaced by the snapped value.
    """
    ref_index = pd.DatetimeIndex(
        sorted(set(pd.to_datetime(list(reference_times))))
    )
    if len(ref_index) == 0:
        return df.iloc[0:0].copy()

    if method == "exact":
        return df[df["time"].isin(ref_index)].reset_index(drop=True)

    if method != "nearest":
        raise ValueError(f"Unknown alignment method: {method!r}")

    ref_df = pd.DataFrame({"aligned_time": ref_index}).sort_values("aligned_time")
    df_sorted = df.sort_values("time").copy()

    # Normalize datetime resolution so merge_asof doesn't reject mismatched
    # dtypes (e.g. ns vs us, which arise when mixing xarray and newer pandas).
    df_sorted["time"] = df_sorted["time"].astype("datetime64[us]")
    ref_df["aligned_time"] = ref_df["aligned_time"].astype("datetime64[us]")

    tol = (
        pd.Timedelta(tolerance)
        if tolerance is not None and not isinstance(tolerance, pd.Timedelta)
        else tolerance
    )

    snapped = pd.merge_asof(
        df_sorted,
        ref_df,
        left_on="time",
        right_on="aligned_time",
        direction="nearest",
        tolerance=tol,
    )
    snapped = snapped.dropna(subset=["aligned_time"]).copy()
    snapped["time"] = snapped["aligned_time"]
    return snapped.drop(columns=["aligned_time"]).reset_index(drop=True)


def fix_cams_time(ds: xr.Dataset, base_date: str) -> xr.Dataset:
    """
    Re-encode the CAMS European-AQ time axis as proper timestamps.

    The CAMS file delivered by ADS uses a non-standard time encoding (the
    ``time`` coord is hours-since-the-analysis-base-date stored as a bare
    float, with no CF ``units`` attribute), so xarray cannot decode it on
    open.  This helper attaches the missing context and returns a dataset
    with a real ``datetime64`` time axis.

    Parameters
    ----------
    ds : xarray.Dataset
        Dataset opened from a CAMS analysis NetCDF file.
    base_date : str
        The date the file's ANALYSIS attribute refers to, e.g. "2024-06-15".
    """
    if "time" not in ds.coords:
        return ds

    time_values = ds["time"].values
    # If xarray already decoded the time axis to datetime64, leave it alone —
    # otherwise we'd reinterpret nanosecond integers as "hours" and overflow.
    if np.issubdtype(time_values.dtype, np.datetime64):
        return ds

    hours = np.asarray(time_values, dtype="float64")
    real_times = pd.Timestamp(base_date) + pd.to_timedelta(hours, unit="h")
    return ds.assign_coords(time=("time", real_times.to_numpy()))
