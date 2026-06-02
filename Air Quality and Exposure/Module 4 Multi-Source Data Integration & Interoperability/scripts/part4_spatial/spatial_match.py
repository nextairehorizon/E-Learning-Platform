from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
import xarray as xr


# ---------------------------------------------------------------------------
# Conventions used throughout this module
# ---------------------------------------------------------------------------
#
# Coordinates    : decimal degrees latitude / longitude, EPSG:4326 (WGS84).
#                  Both CAMS and ERA5 deliver fields on WGS84 grids, so the
#                  notebook does *not* reproject — it only checks consistency.
#
# Grid coords    : xarray DataArrays / Datasets carrying ``latitude`` /
#                  ``longitude`` (or ``lat`` / ``lon``) coordinates.  No
#                  CRS attribute is required; the helpers below treat the
#                  axes as WGS84 unless told otherwise.
#
# Stations       : pandas DataFrames with at least ``location_id``, ``lat``,
#                  ``lon`` columns in decimal degrees.
#
# Output schema  : the canonical long format used everywhere in this project:
#                  time, location_id, lat, lon, variable, value, source,
#                  method.  Identical to Parts 1 and 2 so the spatial output
#                  can be concatenated with theirs without remapping columns.


LAT_CANDIDATES = ["latitude", "lat", "LAT", "Latitude"]
LON_CANDIDATES = ["longitude", "lon", "LON", "Longitude"]


# ---------------------------------------------------------------------------
# 1. CRS check
# ---------------------------------------------------------------------------
@dataclass
class CRSReport:
    """Lightweight result of :func:`crs_check`."""
    ok: bool
    grid_crs: str
    stations_crs: str
    issues: list[str]

    def __bool__(self) -> bool:
        return self.ok


def crs_check(
    grid,
    stations: pd.DataFrame,
    *,
    expected_crs: str = "EPSG:4326",
    lat_bounds: tuple[float, float] = (-90.0, 90.0),
    lon_bounds: tuple[float, float] = (-180.0, 180.0),
) -> CRSReport:
    """
    Verify that the grid and the station table share a coordinate system and
    that station coordinates fall inside the grid's footprint.

    The check is deliberately *lightweight*: it does not reproject anything,
    it only flags inconsistencies so the caller can decide what to do.

    What is checked
    ---------------
    1. Both inputs declare (or default to) the same CRS.  ``expected_crs``
       is ``EPSG:4326`` — the WGS84 lat/lon used by CAMS and ERA5.
    2. Grid coordinates look like WGS84 (lat in [-90, 90], lon in
       [-180, 180] or [0, 360]).  Out-of-range values usually mean a
       projected CRS was opened without reprojecting.
    3. Every station's ``lat``/``lon`` falls inside the grid bounding box.
       Stations outside the box would silently snap to the grid edge with
       ``method="nearest"`` and produce misleading values.

    Parameters
    ----------
    grid : xarray.Dataset or xarray.DataArray
        Gridded field to check.  Must carry a latitude and longitude
        coordinate (any of the conventional names).
    stations : DataFrame
        Must contain ``lat`` and ``lon`` columns in decimal degrees.
    expected_crs : str, default ``"EPSG:4326"``
        The CRS both inputs are expected to be in.  Treated as a string
        comparison only — this module does not reproject.
    lat_bounds, lon_bounds : tuple of float
        Sanity ranges for latitude and longitude values.

    Returns
    -------
    CRSReport
        ``ok=True`` if all three checks pass.  Otherwise ``issues`` lists
        what failed.
    """
    issues: list[str] = []

    grid_crs = str(grid.attrs.get("crs", expected_crs))
    stations_crs = expected_crs  # plain DataFrames have no CRS attribute

    if grid_crs != expected_crs:
        issues.append(
            f"Grid CRS is {grid_crs!r}, expected {expected_crs!r}. "
            "Reproject the grid (or the stations) before extracting."
        )

    lat_name, lon_name = _find_lat_lon(grid)
    lats = np.asarray(grid[lat_name].values)
    lons = np.asarray(grid[lon_name].values)

    if lats.min() < lat_bounds[0] or lats.max() > lat_bounds[1]:
        issues.append(
            f"Grid latitudes range [{lats.min():.3f}, {lats.max():.3f}] "
            f"fall outside {lat_bounds} — looks like a projected CRS."
        )

    # Allow either [-180, 180] (typical) or [0, 360] (some global products).
    lon_min, lon_max = float(lons.min()), float(lons.max())
    in_signed = lon_bounds[0] <= lon_min and lon_max <= lon_bounds[1]
    in_zero_360 = 0.0 <= lon_min and lon_max <= 360.0
    if not (in_signed or in_zero_360):
        issues.append(
            f"Grid longitudes range [{lon_min:.3f}, {lon_max:.3f}] "
            f"fall outside both [-180, 180] and [0, 360]."
        )

    s_lats = pd.to_numeric(stations["lat"], errors="coerce")
    s_lons = pd.to_numeric(stations["lon"], errors="coerce")

    if s_lats.min() < lat_bounds[0] or s_lats.max() > lat_bounds[1]:
        issues.append(
            f"Station latitudes range [{s_lats.min():.3f}, {s_lats.max():.3f}] "
            f"fall outside {lat_bounds}."
        )
    if s_lons.min() < lon_bounds[0] or s_lons.max() > lon_bounds[1]:
        issues.append(
            f"Station longitudes range [{s_lons.min():.3f}, {s_lons.max():.3f}] "
            f"fall outside {lon_bounds}."
        )

    # Footprint containment.  Convert station lons to the grid's convention
    # before comparing so a [0, 360] grid does not falsely reject signed lons.
    s_lons_grid = s_lons.copy()
    if in_zero_360 and not in_signed:
        s_lons_grid = s_lons_grid.where(s_lons_grid >= 0, s_lons_grid + 360.0)

    outside = stations[
        (s_lats < lats.min())
        | (s_lats > lats.max())
        | (s_lons_grid < lons.min())
        | (s_lons_grid > lons.max())
    ]
    if not outside.empty:
        ids = ", ".join(outside["location_id"].astype(str).head(5).tolist())
        more = "" if len(outside) <= 5 else f" (+ {len(outside) - 5} more)"
        issues.append(
            f"{len(outside)} station(s) lie outside the grid footprint: "
            f"{ids}{more}.  Nearest-neighbour would snap them to the edge."
        )

    return CRSReport(
        ok=not issues,
        grid_crs=grid_crs,
        stations_crs=stations_crs,
        issues=issues,
    )


# ---------------------------------------------------------------------------
# 2. Nearest grid value
# ---------------------------------------------------------------------------
def nearest_grid_value(
    grid: xr.Dataset | xr.DataArray,
    variable: str | None,
    stations: pd.DataFrame,
    *,
    source: str | None = None,
) -> pd.DataFrame:
    """
    For each station, take the value of the closest grid cell.

    The cheapest mapping and the right default when the grid resolution is
    fine compared to the gradients in the field (e.g. ERA5 0.25° for
    smooth meteorological variables, CAMS 0.1° for PM₂.₅ at city scale).

    Parameters
    ----------
    grid : xarray.Dataset or DataArray
        Gridded source.  Must have a latitude and longitude coordinate.
    variable : str or None
        Name of the variable to extract.  Pass ``None`` when ``grid`` is
        already a DataArray (the variable name is then taken from it).
    stations : DataFrame
        Output of :func:`station_registry_builder.load_registry`, or any
        frame with ``location_id``, ``lat``, ``lon``.
    source : str, optional
        Override the source label written into the output.

    Returns
    -------
    DataFrame in canonical long format (see module docstring).
    """
    da = _as_dataarray(grid, variable)
    lat_name, lon_name = _find_lat_lon(da)

    station_lats = xr.DataArray(stations["lat"].values, dims="station")
    station_lons = xr.DataArray(stations["lon"].values, dims="station")

    picked = da.sel(
        {lat_name: station_lats, lon_name: station_lons}, method="nearest"
    )

    return _to_long(
        picked=picked,
        stations=stations,
        variable=da.name or (variable or "value"),
        source=source or _infer_source(grid),
        method="nearest",
    )


# ---------------------------------------------------------------------------
# 3. Bilinear grid value (optional)
# ---------------------------------------------------------------------------
def bilinear_grid_value(
    grid: xr.Dataset | xr.DataArray,
    variable: str | None,
    stations: pd.DataFrame,
    *,
    source: str | None = None,
) -> pd.DataFrame:
    """
    For each station, bilinearly interpolate the four surrounding grid cells.

    Use for **smooth, continuous fields** (temperature, pressure, wind
    components).  Avoid for accumulations (precipitation), categorical
    layers (land cover), or quantities with sharp local maxima — bilinear
    interpolation will introduce non-physical values.
    """
    da = _as_dataarray(grid, variable)
    lat_name, lon_name = _find_lat_lon(da)

    # interp needs monotonic coords; sort once.
    da_sorted = da.sortby([lat_name, lon_name])

    station_lats = xr.DataArray(stations["lat"].values, dims="station")
    station_lons = xr.DataArray(stations["lon"].values, dims="station")

    picked = da_sorted.interp(
        {lat_name: station_lats, lon_name: station_lons}
    )

    return _to_long(
        picked=picked,
        stations=stations,
        variable=da.name or (variable or "value"),
        source=source or _infer_source(grid),
        method="bilinear",
    )


# ---------------------------------------------------------------------------
# 4. Buffer average (optional)
# ---------------------------------------------------------------------------
def buffer_average(
    grid: xr.Dataset | xr.DataArray,
    variable: str | None,
    stations: pd.DataFrame,
    *,
    radius_km: float = 10.0,
    source: str | None = None,
) -> pd.DataFrame:
    """
    Average grid values inside a circle of ``radius_km`` around each station.

    Useful when:
      - the station is meant to be regionally representative (rural sites),
      - the grid is coarse compared to local variability,
      - the station's exact coordinates are uncertain (a few hundred metres),
      - you want to smooth single-pixel outliers.

    Distances are computed on a *flat-Earth* approximation
    (1° lat ≈ 111 km, 1° lon ≈ 111 km × cos(lat)).  This is fine up to
    a few hundred kilometres around mid-latitudes; for global coverage
    or very large radii, replace with a proper geodesic distance.

    Parameters
    ----------
    radius_km : float, default 10
        Radius of the averaging buffer in kilometres.

    Returns
    -------
    DataFrame in canonical long format with ``method="buffer_mean_{R}km"``.
    """
    da = _as_dataarray(grid, variable)
    lat_name, lon_name = _find_lat_lon(da)
    lat_values = np.asarray(da[lat_name].values)
    lon_values = np.asarray(da[lon_name].values)

    source_label = source or _infer_source(grid)
    var_name = da.name or (variable or "value")
    rows: list[dict] = []

    for _, station in stations.iterrows():
        dlat_km = (lat_values - station["lat"]) * 111.0
        dlon_km = (lon_values - station["lon"]) * 111.0 * np.cos(
            np.deg2rad(station["lat"])
        )
        dist_km = np.sqrt(dlat_km[:, None] ** 2 + dlon_km[None, :] ** 2)

        inside = xr.DataArray(
            dist_km <= radius_km,
            dims=(lat_name, lon_name),
            coords={lat_name: lat_values, lon_name: lon_values},
        )

        if not bool(inside.any()):
            # Station too far from the grid: nothing inside the buffer.
            rows.append({
                "time": pd.NaT,
                "location_id": station["location_id"],
                "lat": float(station["lat"]),
                "lon": float(station["lon"]),
                "variable": var_name,
                "value": float("nan"),
                "source": source_label,
                "method": f"buffer_mean_{radius_km:g}km",
            })
            continue

        buffered = da.where(inside).mean(
            dim=(lat_name, lon_name), skipna=True
        )

        for t_value, v_value in _iter_time_values(buffered):
            rows.append({
                "time": t_value,
                "location_id": station["location_id"],
                "lat": float(station["lat"]),
                "lon": float(station["lon"]),
                "variable": var_name,
                "value": v_value,
                "source": source_label,
                "method": f"buffer_mean_{radius_km:g}km",
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 5. Optional: vector spatial join (e.g. land use)
# ---------------------------------------------------------------------------
def join_contextual_layer(
    stations: pd.DataFrame,
    layer_path: str,
    *,
    attribute: str,
    method: str = "intersect",
    buffer_m: float = 0.0,
    stations_crs: str = "EPSG:4326",
) -> pd.DataFrame:
    """
    Attach a single attribute from a vector layer (FlatGeobuf, GeoPackage,
    shapefile, ...) to each station.

    This is the only function in the module that imports GeoPandas, and it
    is only used when contextual layers are available.

    Parameters
    ----------
    stations : DataFrame
        Must contain ``location_id``, ``lat``, ``lon``.
    layer_path : str
        Path readable by ``geopandas.read_file`` (FGB, GPKG, SHP, ...).
    attribute : str
        Name of the column on the layer to attach to each station.
    method : {"intersect", "nearest"}
        ``intersect`` keeps the attribute of the polygon (or buffered
        point's intersector) the station falls into.  ``nearest`` keeps
        the attribute of the closest feature.
    buffer_m : float, default 0
        If positive, the station point is first buffered to this radius
        (in metres, in the **layer's** CRS) before the join — useful for
        polygon layers when the station is close to a class boundary.
    stations_crs : str, default ``"EPSG:4326"``

    Returns
    -------
    DataFrame with the original station columns plus ``attribute``.
    """
    import geopandas as gpd
    from shapely.geometry import Point

    layer = gpd.read_file(layer_path)
    if attribute not in layer.columns:
        raise KeyError(
            f"Attribute {attribute!r} not in layer columns: {list(layer.columns)}"
        )

    pts = gpd.GeoDataFrame(
        stations.copy(),
        geometry=[Point(lon, lat) for lat, lon in zip(stations["lat"], stations["lon"])],
        crs=stations_crs,
    ).to_crs(layer.crs)

    if buffer_m > 0:
        pts["geometry"] = pts.geometry.buffer(buffer_m)

    if method == "intersect":
        joined = gpd.sjoin(
            pts, layer[[attribute, "geometry"]], how="left", predicate="intersects"
        )
        joined = joined.drop(columns=[c for c in ("index_right",) if c in joined.columns])
    elif method == "nearest":
        joined = gpd.sjoin_nearest(
            pts, layer[[attribute, "geometry"]], how="left"
        )
        joined = joined.drop(columns=[c for c in ("index_right",) if c in joined.columns])
    else:
        raise ValueError(f"Unknown join method: {method!r}")

    out = pd.DataFrame(joined.drop(columns="geometry"))
    return out


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _find_lat_lon(obj) -> tuple[str, str]:
    coords = getattr(obj, "coords", {})
    dims = getattr(obj, "dims", ())
    available = set(coords) | set(dims)

    lat = next((n for n in LAT_CANDIDATES if n in available), None)
    lon = next((n for n in LON_CANDIDATES if n in available), None)
    if lat is None or lon is None:
        raise ValueError(
            f"Could not find latitude/longitude coordinates.  "
            f"Tried {LAT_CANDIDATES} / {LON_CANDIDATES}; available: {sorted(available)}"
        )
    return lat, lon


def _as_dataarray(
    grid: xr.Dataset | xr.DataArray, variable: str | None
) -> xr.DataArray:
    if isinstance(grid, xr.DataArray):
        return grid
    if not isinstance(grid, xr.Dataset):
        raise TypeError(
            f"`grid` must be xarray.Dataset or DataArray, got {type(grid).__name__}"
        )
    if variable is None:
        raise ValueError("variable= is required when grid is a Dataset.")
    if variable not in grid.data_vars:
        raise KeyError(
            f"Variable {variable!r} not in dataset.  "
            f"Available: {list(grid.data_vars)}"
        )
    return grid[variable]


def _infer_source(grid) -> str:
    attrs = getattr(grid, "attrs", {}) or {}
    for key in ("product_name", "source", "title"):
        v = attrs.get(key)
        if v:
            return str(v)
    return "grid"


def _iter_time_values(da: xr.DataArray) -> Iterable[tuple[pd.Timestamp, float]]:
    """Yield (time, value) pairs from a DataArray with at most one ``time`` dim."""
    da = da.squeeze(drop=True)
    if "time" in da.dims:
        for t in da["time"].values:
            yield pd.Timestamp(t), float(da.sel(time=t).values)
    else:
        yield pd.NaT, float(da.values)


def _to_long(
    picked: xr.DataArray,
    stations: pd.DataFrame,
    variable: str,
    source: str,
    method: str,
) -> pd.DataFrame:
    picked = picked.squeeze(drop=True)

    if "time" not in picked.dims:
        picked = picked.expand_dims("time")

    picked = picked.reset_coords(drop=True)
    df = picked.to_dataframe(name="value").reset_index()

    # Drop any grid lat/lon columns carried along on the station dim so the
    # merge with station coords below does not produce lat_x/lon_x suffixes.
    grid_cols = [c for c in df.columns if c in ("lat", "lon", "latitude", "longitude")]
    if grid_cols:
        df = df.drop(columns=grid_cols)

    stations_indexed = stations.reset_index().rename(columns={"index": "station"})
    df = df.merge(
        stations_indexed[["station", "location_id", "lat", "lon"]], on="station"
    )

    df["variable"] = variable
    df["source"] = source
    df["method"] = method
    df["time"] = pd.to_datetime(df["time"], errors="coerce")

    return df[
        ["time", "location_id", "lat", "lon", "variable", "value", "source", "method"]
    ]
