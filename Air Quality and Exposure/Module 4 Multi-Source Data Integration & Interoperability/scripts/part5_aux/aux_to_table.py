from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

import pandas as pd


# ---------------------------------------------------------------------------
# Dataset contracts
# ---------------------------------------------------------------------------
#
# A "contract" is the explicit agreement between an auxiliary feed and the
# integration pipeline: which columns must be present, what units they are
# in, which version of the dataset this is, and how to label it in the
# canonical long format.
#
# Writing contracts down means:
#
#   - the adapter author and the integration author do not silently disagree
#     about units or column meaning;
#   - upstream schema changes fail loudly at the contract check instead of
#     producing wrong numbers downstream;
#   - the same `to_canonical_long` helper handles every feed.

CANONICAL_COLUMNS = [
    "time",
    "location_id",
    "lat",
    "lon",
    "variable",
    "value",
    "source",
    "method",
]


@dataclass
class DatasetContract:
    """
    Declarative description of one auxiliary feed.

    Attributes
    ----------
    name : str
        Human-readable name (used in error messages and reports).
    source : str
        The string written into the ``source`` column of the canonical
        long table — e.g. ``"traffic_counters"`` or ``"station_meteo"``.
    version : str
        Free-form version tag (date, semver, vendor build).  Carried
        through into the output as ``dataset_version`` so anyone can
        retrace which release a value came from.
    method : str
        How the value reaches a station: ``"colocated"`` (sensor at the
        site), ``"nearest_counter"`` (assigned by proximity), ``"static"``
        (per-station constant), ...
    required_columns : list of str
        Columns the adapter must produce.  Missing any of them is an
        error.
    value_columns : dict[str, str]
        ``{adapter_column: canonical_variable_name}``.  The adapter
        column carries the numeric value; the canonical name is what
        lands in the ``variable`` column.  E.g.
        ``{"temperature_c": "temp_station"}``.
    units : dict[str, str]
        ``{canonical_variable_name: unit_string}`` — recorded in the
        metadata sidecar, not validated numerically.
    """

    name: str
    source: str
    version: str
    method: str
    required_columns: list[str]
    value_columns: Mapping[str, str]
    units: Mapping[str, str] = field(default_factory=dict)
    static: bool = False  # True for per-station constants (no `time` axis)


# ---------------------------------------------------------------------------
# Ready-made contracts for the teaching pipeline
# ---------------------------------------------------------------------------
TRAFFIC_CONTRACT = DatasetContract(
    name="Hourly traffic counters",
    source="traffic_counters",
    version="synth-2024-06",
    method="colocated",
    required_columns=["location_id", "time", "vehicle_count", "speed_kmh", "heavy_fraction"],
    value_columns={
        "vehicle_count": "traffic_count_h",
        "speed_kmh": "traffic_speed_kmh",
        "heavy_fraction": "traffic_heavy_frac",
    },
    units={
        "traffic_count_h": "vehicles/hour",
        "traffic_speed_kmh": "km/h",
        "traffic_heavy_frac": "dimensionless (0-1)",
    },
)

STATION_METEO_CONTRACT = DatasetContract(
    name="Station-colocated meteorology",
    source="station_meteo",
    version="synth-2024-06",
    method="colocated",
    required_columns=[
        "location_id", "time", "temperature_c", "humidity_pct", "wind_speed_ms",
    ],
    value_columns={
        "temperature_c": "temp_station",
        "humidity_pct": "rh_station",
        "wind_speed_ms": "wind_station",
        "wind_dir_deg": "wind_dir_station",
        "pressure_hpa": "pressure_station",
    },
    units={
        "temp_station": "degC",
        "rh_station": "percent",
        "wind_station": "m/s",
        "wind_dir_station": "degrees from N",
        "pressure_station": "hPa",
    },
)

STATIC_CONTEXT_CONTRACT = DatasetContract(
    name="Static per-station context",
    source="static_context",
    version="synth-2024-06",
    method="static",
    required_columns=["location_id"],
    value_columns={
        "elevation_m": "elevation",
        "land_use_code": "land_use_code",
        "lcz_class": "lcz_class",
        "road_dist_m": "road_distance",
        "energy_intensity_kwh_m2": "energy_intensity",
    },
    units={
        "elevation": "m",
        "land_use_code": "Urban Atlas code_2021",
        "lcz_class": "Local Climate Zone (1-17)",
        "road_distance": "m",
        "energy_intensity": "kWh/m^2/year",
    },
    static=True,
)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
@dataclass
class ContractReport:
    ok: bool
    name: str
    missing_columns: list[str]
    issues: list[str]

    def __bool__(self) -> bool:
        return self.ok


def validate_contract(df: pd.DataFrame, contract: DatasetContract) -> ContractReport:
    """
    Check that ``df`` satisfies ``contract``.

    Validates:

    - every required column is present,
    - at least one of the contract's ``value_columns`` is present,
    - the ``time`` column exists for non-static contracts and parses
      cleanly,
    - ``location_id`` exists.
    """
    issues: list[str] = []
    missing = [c for c in contract.required_columns if c not in df.columns]
    if missing:
        issues.append(
            f"[{contract.name}] missing required columns: {missing}"
        )

    val_present = [c for c in contract.value_columns if c in df.columns]
    if not val_present:
        issues.append(
            f"[{contract.name}] none of the value columns "
            f"{list(contract.value_columns)} are present."
        )

    if "location_id" not in df.columns:
        issues.append(f"[{contract.name}] `location_id` column is required.")

    if not contract.static:
        if "time" not in df.columns:
            issues.append(f"[{contract.name}] `time` column is required.")
        else:
            try:
                pd.to_datetime(df["time"], errors="raise")
            except Exception as e:
                issues.append(f"[{contract.name}] `time` does not parse: {e}")

    return ContractReport(
        ok=not issues,
        name=contract.name,
        missing_columns=missing,
        issues=issues,
    )


# ---------------------------------------------------------------------------
# Canonical-schema conversion
# ---------------------------------------------------------------------------
def to_canonical_long(
    df: pd.DataFrame,
    contract: DatasetContract,
    stations: pd.DataFrame,
    *,
    source_tz: str | None = None,
    target_tz: str = "UTC",
) -> pd.DataFrame:
    """
    Convert an adapter's tidy DataFrame into the project's canonical
    long-format schema.

    The output schema matches Parts 1 - 4 verbatim, with one extra
    ``dataset_version`` column for provenance:

        time, location_id, lat, lon, variable, value, source, method,
        dataset_version

    Static contracts (``contract.static=True``) produce rows with
    ``time = NaT``; downstream join code attaches them to every
    ``(time, location_id)`` row on ``location_id`` alone.

    Parameters
    ----------
    df : DataFrame
        Output of one of the ``ingest_*`` adapters.
    contract : DatasetContract
        The contract this feed satisfies.  Validated before conversion.
    stations : DataFrame
        Registry with at least ``location_id``, ``lat``, ``lon``.
    source_tz : str, optional
        IANA name of the time zone the timestamps are in if they are
        tz-naive.  Default ``None`` -> assumed to already be in UTC.
    target_tz : str, default ``"UTC"``
    """
    report = validate_contract(df, contract)
    if not report:
        raise ValueError(
            f"Contract {contract.name!r} not satisfied:\n  - "
            + "\n  - ".join(report.issues)
        )

    out = df.copy()

    if not contract.static:
        t = pd.to_datetime(out["time"], errors="coerce")
        if t.dt.tz is None:
            if source_tz is not None:
                t = t.dt.tz_localize(source_tz, ambiguous="infer", nonexistent="shift_forward")
                t = t.dt.tz_convert(target_tz)
            else:
                t = t.dt.tz_localize(target_tz)
        else:
            t = t.dt.tz_convert(target_tz)
        out["time"] = t
    else:
        out["time"] = pd.NaT

    # Attach lat/lon from the registry (the adapter is not required to
    # carry them — only `location_id` is mandatory).
    loc_cols = ["location_id"] + [
        c for c in ("lat", "lon") if c in stations.columns
    ]
    out = out.merge(stations[loc_cols], on="location_id", how="left", suffixes=("", "_reg"))
    for col in ("lat", "lon"):
        if col in out.columns and f"{col}_reg" in out.columns:
            out[col] = out[col].fillna(out[f"{col}_reg"])
            out = out.drop(columns=[f"{col}_reg"])
        elif f"{col}_reg" in out.columns:
            out = out.rename(columns={f"{col}_reg": col})

    pieces: list[pd.DataFrame] = []
    for adapter_col, var_name in contract.value_columns.items():
        if adapter_col not in out.columns:
            continue
        piece = out[["time", "location_id", "lat", "lon", adapter_col]].copy()
        piece = piece.rename(columns={adapter_col: "value"})
        piece["variable"] = var_name
        piece["source"] = contract.source
        piece["method"] = contract.method
        piece["dataset_version"] = contract.version
        pieces.append(piece)

    if not pieces:
        raise ValueError(
            f"No value columns from contract {contract.name!r} were "
            f"present in the input."
        )

    long = pd.concat(pieces, ignore_index=True)
    cols = CANONICAL_COLUMNS + ["dataset_version"]
    return long[cols]
