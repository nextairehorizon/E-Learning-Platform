from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


# ---------------------------------------------------------------------------
# The station registry
# ---------------------------------------------------------------------------
#
# A *station registry* is the canonical list of monitoring sites the
# integration pipeline knows about.  Parts 1, 2 and 3 use a minimal
# 3-column form (``location_id``, ``lat``, ``lon``); Part 4 enriches it
# with the descriptive metadata that the spatial step actually needs:
#
#   - ``type``        — what kind of site this is (background / traffic /
#                       industrial / rural / suburban / unknown).  Drives
#                       the choice of mapping method (e.g. buffer-mean for
#                       rural background, nearest for urban traffic).
#   - ``height_m``    — sensor inlet height above ground in metres.
#                       Useful when comparing against gridded products at
#                       different reference heights (e.g. CAMS surface vs
#                       ERA5 2 m).
#   - ``notes``       — free text: known issues, microenvironment notes,
#                       construction work nearby, etc.
#
# The registry stays in WGS84 (EPSG:4326) decimal degrees throughout.

REQUIRED_COLUMNS = ["location_id", "lat", "lon"]
OPTIONAL_COLUMNS = ["station_name", "country", "type", "height_m", "notes"]
ALLOWED_TYPES = {
    "background",
    "traffic",
    "industrial",
    "rural",
    "suburban",
    "urban",
    "unknown",
}


# ---------------------------------------------------------------------------
# Validation result
# ---------------------------------------------------------------------------
@dataclass
class RegistryReport:
    """Result of :func:`validate_registry` — a structured QA summary."""
    ok: bool
    n_rows: int
    duplicates: list[str]
    out_of_range: list[str]
    unknown_types: list[str]
    issues: list[str]

    def __bool__(self) -> bool:
        return self.ok


# ---------------------------------------------------------------------------
# Build a registry
# ---------------------------------------------------------------------------
def build_registry(
    base: pd.DataFrame,
    *,
    defaults: dict | None = None,
    overrides: dict[str, dict] | None = None,
) -> pd.DataFrame:
    """
    Build a station registry from a base table of stations.

    Starts from the project-wide ``stations_example.csv`` (or any
    equivalent minimal table with ``location_id``, ``lat``, ``lon``) and
    fills in the optional descriptive columns:

    - column-level defaults via ``defaults``
      (e.g. ``defaults={"type": "background"}``),
    - per-station overrides via ``overrides``
      (e.g. ``overrides={"ZAGREB01": {"type": "traffic", "height_m": 3.0}}``).

    Missing optional columns are added with sensible defaults
    (``type="unknown"``, ``height_m=NaN``, ``notes=""``).

    Parameters
    ----------
    base : DataFrame
        Must contain ``location_id``, ``lat``, ``lon``.
    defaults : dict, optional
        ``{column: value}`` applied to every row that does not already
        have a value in that column.
    overrides : dict, optional
        ``{location_id: {column: value, ...}}``.  Applied after
        ``defaults``, so per-station values win.

    Returns
    -------
    DataFrame with the full registry schema:
        location_id, station_name, country, lat, lon, type, height_m, notes
    """
    missing = set(REQUIRED_COLUMNS) - set(base.columns)
    if missing:
        raise ValueError(
            f"Base table is missing required columns: {sorted(missing)}.  "
            f"Found: {list(base.columns)}"
        )

    reg = base.copy()
    for col in OPTIONAL_COLUMNS:
        if col not in reg.columns:
            if col == "height_m":
                reg[col] = pd.NA
            elif col == "notes":
                reg[col] = ""
            elif col == "type":
                reg[col] = "unknown"
            else:
                reg[col] = ""

    if defaults:
        for col, val in defaults.items():
            if col not in reg.columns:
                reg[col] = val
                continue
            mask = reg[col].isna() | (reg[col].astype(str) == "") | (
                reg[col].astype(str) == "unknown"
            )
            reg.loc[mask, col] = val

    if overrides:
        for loc_id, fields in overrides.items():
            mask = reg["location_id"].astype(str) == str(loc_id)
            if not mask.any():
                # Skipped silently — the caller may have provided overrides
                # for sites that are not in this particular base table.
                continue
            for col, val in fields.items():
                if col not in reg.columns:
                    reg[col] = pd.NA
                reg.loc[mask, col] = val

    ordered = ["location_id", "station_name", "country",
               "lat", "lon", "type", "height_m", "notes"]
    final_cols = [c for c in ordered if c in reg.columns] + [
        c for c in reg.columns if c not in ordered
    ]
    return reg[final_cols].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Validate a registry
# ---------------------------------------------------------------------------
def validate_registry(
    registry: pd.DataFrame,
    *,
    lat_bounds: tuple[float, float] = (-90.0, 90.0),
    lon_bounds: tuple[float, float] = (-180.0, 180.0),
) -> RegistryReport:
    """
    Check that the registry is internally consistent.

    Fails when:

    - a required column is missing,
    - ``location_id`` values are duplicated,
    - any ``lat`` / ``lon`` falls outside the WGS84 ranges,
    - any ``type`` is not in :data:`ALLOWED_TYPES`.

    Returns
    -------
    RegistryReport
        ``ok=True`` if the registry passes every check.
    """
    issues: list[str] = []

    missing = set(REQUIRED_COLUMNS) - set(registry.columns)
    if missing:
        issues.append(
            f"Missing required columns: {sorted(missing)}."
        )
        return RegistryReport(
            ok=False,
            n_rows=len(registry),
            duplicates=[],
            out_of_range=[],
            unknown_types=[],
            issues=issues,
        )

    dup_mask = registry["location_id"].duplicated(keep=False)
    duplicates = registry.loc[dup_mask, "location_id"].astype(str).unique().tolist()
    if duplicates:
        issues.append(f"Duplicate location_id values: {duplicates}.")

    lats = pd.to_numeric(registry["lat"], errors="coerce")
    lons = pd.to_numeric(registry["lon"], errors="coerce")
    out_of_range_mask = (
        lats.isna()
        | lons.isna()
        | (lats < lat_bounds[0]) | (lats > lat_bounds[1])
        | (lons < lon_bounds[0]) | (lons > lon_bounds[1])
    )
    out_of_range = registry.loc[
        out_of_range_mask, "location_id"
    ].astype(str).tolist()
    if out_of_range:
        issues.append(
            f"{len(out_of_range)} station(s) have invalid coordinates: "
            f"{out_of_range[:5]}{'...' if len(out_of_range) > 5 else ''}."
        )

    unknown_types: list[str] = []
    if "type" in registry.columns:
        bad_mask = ~registry["type"].astype(str).isin(ALLOWED_TYPES)
        unknown_types = registry.loc[bad_mask, "location_id"].astype(str).tolist()
        if unknown_types:
            bad_values = sorted(set(registry.loc[bad_mask, "type"].astype(str)))
            issues.append(
                f"{len(unknown_types)} station(s) have non-standard `type` "
                f"({bad_values}).  Allowed: {sorted(ALLOWED_TYPES)}."
            )

    return RegistryReport(
        ok=not issues,
        n_rows=len(registry),
        duplicates=duplicates,
        out_of_range=out_of_range,
        unknown_types=unknown_types,
        issues=issues,
    )


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------
def load_registry(csv_path: str) -> pd.DataFrame:
    """
    Load a registry CSV with coordinate sanity checks.

    Required columns: ``location_id``, ``lat``, ``lon``.  Optional columns
    are kept verbatim if present.
    """
    df = pd.read_csv(csv_path)
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(
            f"Registry file {csv_path} is missing required columns: "
            f"{sorted(missing)}.  Found: {list(df.columns)}"
        )

    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df.dropna(subset=["lat", "lon"]).reset_index(drop=True)
    return df


def save_registry(registry: pd.DataFrame, csv_path: str) -> None:
    """
    Save a registry to CSV in the canonical column order.

    Validates before writing — refuses to persist a malformed registry.
    """
    report = validate_registry(registry)
    if not report:
        raise ValueError(
            "Refusing to save invalid registry:\n  - "
            + "\n  - ".join(report.issues)
        )
    registry.to_csv(csv_path, index=False)


def print_report(report: RegistryReport) -> None:
    """Pretty-print a :class:`RegistryReport` in a notebook-friendly way."""
    status = "OK" if report.ok else "ISSUES FOUND"
    print(f"Registry validation: {status}  ({report.n_rows} rows)")
    if report.ok:
        return
    for line in report.issues:
        print(f"  - {line}")
