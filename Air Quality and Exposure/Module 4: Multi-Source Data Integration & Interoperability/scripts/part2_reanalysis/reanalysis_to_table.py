from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import xarray as xr


CANONICAL_COLUMNS = [
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


def to_canonical(df: pd.DataFrame) -> pd.DataFrame:
    """
    Make sure the DataFrame has the canonical columns, in the canonical order,
    in the canonical dtypes.  Missing columns are filled with NaN.

    Extends the Part 1 satellite schema with a ``dataset_version`` column so
    a single reanalysis row carries enough provenance for reproducibility.
    """
    out = df.copy()

    for col in CANONICAL_COLUMNS:
        if col not in out.columns:
            out[col] = pd.NA

    out = out[CANONICAL_COLUMNS]

    out["time"] = pd.to_datetime(out["time"], errors="coerce", utc=False)
    out["lat"] = pd.to_numeric(out["lat"], errors="coerce")
    out["lon"] = pd.to_numeric(out["lon"], errors="coerce")
    out["value"] = pd.to_numeric(out["value"], errors="coerce")

    for col in ["location_id", "variable", "source", "method", "dataset_version"]:
        out[col] = out[col].astype("string")

    return out


def build_metadata(
    ds: xr.Dataset,
    variables: str | list[str],
    method: str,
    extra: dict | None = None,
) -> dict:
    """
    Pull the most important provenance information for a reanalysis extraction.

    Returns a small dict suitable for writing as a sidecar text file next to
    the canonical CSV.  Keep it short and human-readable.
    """
    if isinstance(variables, str):
        variables = [variables]

    units_per_var = []
    long_names: list[str] = []
    for v in variables:
        if v in ds.data_vars:
            attrs = ds[v].attrs
            units = attrs.get("units", "unknown")
            long_name = attrs.get(
                "long_name", attrs.get("standard_name", "")
            )
            units_per_var.append(f"{v}={units}")
            if long_name:
                long_names.append(f"{v}: {long_name}")

    file_attrs = ds.attrs
    history = str(file_attrs.get("history", "")).strip()
    version = history[:120] if history else file_attrs.get("source", "unknown")

    meta = {
        "dataset_title": file_attrs.get("title", "unknown"),
        "institution": file_attrs.get("institution", "unknown"),
        "source": file_attrs.get("source", "unknown"),
        "dataset_version": version,
        "variables": ", ".join(variables),
        "variable_units": "; ".join(units_per_var) if units_per_var else "unknown",
        "variable_long_names": " | ".join(long_names) if long_names else "",
        "extraction_method": method,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    if extra:
        meta.update(extra)

    return meta


def save_table(
    df: pd.DataFrame,
    output_csv: str | Path,
    metadata: dict | None = None,
) -> Path:
    """
    Save the canonical DataFrame to CSV and write a sidecar metadata file.
    """
    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    df_to_save = to_canonical(df)
    df_to_save.to_csv(output_csv, index=False)

    if metadata:
        meta_path = output_csv.with_suffix(".meta.txt")
        with meta_path.open("w", encoding="utf-8") as f:
            f.write("# Reanalysis extraction - metadata block\n")
            f.write(f"# Companion file for: {output_csv.name}\n")
            f.write("#\n")
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")

    return output_csv


def write_canonical_output(
    extracted_df: pd.DataFrame,
    ds: xr.Dataset,
    variables: str | list[str],
    method: str,
    output_csv: str | Path,
) -> Path:
    """
    One-liner: tidy up the extracted DataFrame, build metadata from the
    dataset, save both files.
    """
    metadata = build_metadata(ds=ds, variables=variables, method=method)
    return save_table(extracted_df, output_csv=output_csv, metadata=metadata)
