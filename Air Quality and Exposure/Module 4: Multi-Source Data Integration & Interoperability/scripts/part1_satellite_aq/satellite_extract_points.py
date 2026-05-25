from __future__ import annotations

import numpy as np
import pandas as pd
import xarray as xr


def load_stations(csv_path: str) -> pd.DataFrame:
    """
    Load a CSV of monitoring stations.

    The CSV must have at least these three columns:
        location_id   -> any unique identifier (text or number)
        lat           -> latitude in decimal degrees, e.g. 38.72
        lon           -> longitude in decimal degrees, e.g. -9.14

    Parameters
    ----------
    csv_path : str
        Path to the stations CSV file.

    Returns
    -------
    pandas.DataFrame
        Cleaned station table.
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
    df = df.dropna(subset=["lat", "lon"]).reset_index(drop=True)

    return df


def _find_coord_names(ds: xr.Dataset) -> tuple[str, str]:
    """
    Different satellite products use different names for latitude/longitude
    (e.g. 'lat', 'latitude', 'LAT').  This helper finds them automatically.
    """
    lat_candidates = ["lat", "latitude", "LAT", "Latitude"]
    lon_candidates = ["lon", "longitude", "LON", "Longitude"]

    lat_name = next((n for n in lat_candidates if n in ds.coords or n in ds.dims), None)
    lon_name = next((n for n in lon_candidates if n in ds.coords or n in ds.dims), None)

    if lat_name is None or lon_name is None:
        raise ValueError(
            "Could not find latitude/longitude coordinates in the dataset. "
            f"Available coordinates: {list(ds.coords)}"
        )
    return lat_name, lon_name


def extract_nearest(
    ds: xr.Dataset,
    variable: str,
    stations: pd.DataFrame,
    qa_variable: str | None = None,
    qa_threshold: float = 0.75,
) -> pd.DataFrame:
    """
    For each station, take the satellite value of the nearest grid pixel.

    Parameters
    ----------
    ds : xarray.Dataset
        Opened satellite dataset (e.g. from ``xr.open_dataset(...)``).
    variable : str
        Name of the variable to extract, e.g. 'no2'.
    stations : pandas.DataFrame
        Output of ``load_stations`` (must have location_id, lat, lon).
    qa_variable : str, optional
        Name of the quality-flag variable, e.g. 'qa_value'.
        If None, no quality filtering is applied.
    qa_threshold : float, default 0.75
        Pixels with qa < threshold are set to NaN.
        (0.75 is the standard TROPOMI recommendation for NO2.)

    Returns
    -------
    pandas.DataFrame
        Long-format table with columns:
        time, location_id, lat, lon, variable, value, source, method
    """
    lat_name, lon_name = _find_coord_names(ds)

    if variable not in ds.data_vars:
        raise KeyError(
            f"Variable '{variable}' not found in dataset. "
            f"Available variables: {list(ds.data_vars)}"
        )
    data = ds[variable]

    if qa_variable is not None:
        if qa_variable not in ds.data_vars:
            raise KeyError(
                f"QA variable '{qa_variable}' not found in dataset. "
                f"Available variables: {list(ds.data_vars)}"
            )
        qa = ds[qa_variable]
        data = data.where(qa >= qa_threshold)

    station_lats = xr.DataArray(stations["lat"].values, dims="station")
    station_lons = xr.DataArray(stations["lon"].values, dims="station")

    picked = data.sel(
        {lat_name: station_lats, lon_name: station_lons},
        method="nearest",
    )

    return _to_long_dataframe(
        picked=picked,
        stations=stations,
        variable=variable,
        source=ds.attrs.get("product_name", "satellite"),
        method="nearest",
    )


def extract_buffer_mean(
    ds: xr.Dataset,
    variable: str,
    stations: pd.DataFrame,
    radius_km: float = 10.0,
    qa_variable: str | None = None,
    qa_threshold: float = 0.75,
) -> pd.DataFrame:
    """
    For each station, average the satellite values inside a circle of
    ``radius_km`` around the station.

    This is useful when:
      - the satellite pixel is smaller than your area of interest
      - you want to smooth out noise
      - the station's exact coordinates are uncertain

    Parameters
    ----------
    ds : xarray.Dataset
    variable : str
    stations : pandas.DataFrame
    radius_km : float, default 10
        Radius of the averaging buffer in kilometres.
    qa_variable, qa_threshold :
        Same as in ``extract_nearest``.

    Returns
    -------
    pandas.DataFrame  (same columns as ``extract_nearest``)
    """
    lat_name, lon_name = _find_coord_names(ds)

    if variable not in ds.data_vars:
        raise KeyError(f"Variable '{variable}' not found in dataset.")
    data = ds[variable]

    if qa_variable is not None and qa_variable in ds.data_vars:
        data = data.where(ds[qa_variable] >= qa_threshold)

    lat_values = ds[lat_name].values 
    lon_values = ds[lon_name].values 

    out_rows = []
    for _, station in stations.iterrows():
        dlat_km = (lat_values - station["lat"]) * 111.0  # 1 deg lat ~= 111 km
        dlon_km = (lon_values - station["lon"]) * 111.0 * np.cos(
            np.deg2rad(station["lat"])
        )

        dist_km = np.sqrt(
            dlat_km[:, None] ** 2 + dlon_km[None, :] ** 2
        )  

        inside = xr.DataArray(
            dist_km <= radius_km,
            dims=(lat_name, lon_name),
            coords={lat_name: lat_values, lon_name: lon_values},
        )

        buffered = data.where(inside).mean(
            dim=(lat_name, lon_name), skipna=True
        )

        for t_value, v_value in _iter_time_values(buffered):
            out_rows.append(
                {
                    "time": t_value,
                    "location_id": station["location_id"],
                    "lat": float(station["lat"]),
                    "lon": float(station["lon"]),
                    "variable": variable,
                    "value": v_value,
                    "source": ds.attrs.get("product_name", "satellite"),
                    "method": f"buffer_mean_{radius_km}km",
                }
            )

    return pd.DataFrame(out_rows)


def _iter_time_values(da: xr.DataArray):
    """Yield (time, value) pairs from a DataArray that has at most one 'time' dim."""
    da = da.squeeze(drop=True)

    if "time" in da.dims:
        for t in da["time"].values:
            v = float(da.sel(time=t).values)
            yield pd.Timestamp(t), v
    else:
        yield pd.NaT, float(da.values)


def _to_long_dataframe(
    picked: xr.DataArray,
    stations: pd.DataFrame,
    variable: str,
    source: str,
    method: str,
) -> pd.DataFrame:
    """Turn an xarray DataArray with dims (time, station) into a long DataFrame.

    Handles extra size-1 dims like CAMS' 'level' transparently by squeezing
    them out before building the DataFrame.
    """
    picked = picked.squeeze(drop=True)

    if "time" not in picked.dims:
        picked = picked.expand_dims("time")

    # The nearest-pixel selection attaches the satellite grid's lat/lon as
    # coords on the station dim; drop them so they don't collide with the
    # station's own lat/lon during the merge below.
    picked = picked.reset_coords(drop=True)

    df = picked.to_dataframe(name="value").reset_index()

    # Some xarray versions still include grid lat/lon as columns even after
    # reset_coords; drop them here so the merge with station coords below
    # doesn't produce lat_x/lon_x suffix collisions.
    grid_coord_cols = [c for c in df.columns if c in ("lat", "lon", "latitude", "longitude")]
    if grid_coord_cols:
        df = df.drop(columns=grid_coord_cols)

    stations_indexed = stations.reset_index().rename(columns={"index": "station"})
    df = df.merge(
        stations_indexed[["station", "location_id", "lat", "lon"]], on="station"
    )

    df["variable"] = variable
    df["source"] = source
    df["method"] = method

    df = df[
        ["time", "location_id", "lat", "lon", "variable", "value", "source", "method"]
    ]

    if df["time"].dtype == "O" and len(df) > 0 and df["time"].iloc[0] == 0:
        df["time"] = pd.NaT
    else:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")

    return df



