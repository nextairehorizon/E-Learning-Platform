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
]


def to_canonical(df: pd.DataFrame) -> pd.DataFrame:
    """
    Make sure the DataFrame has the canonical columns in the canonical order,
    in the canonical dtypes.  Missing columns are filled with NaN.

    This is a 'tidy-up' step you call right before saving.
    """
    out = df.copy()

    for col in CANONICAL_COLUMNS:
        if col not in out.columns:
            out[col] = pd.NA

    out = out[CANONICAL_COLUMNS]

    # Coerce dtypes for safety.
    out["time"] = pd.to_datetime(out["time"], errors="coerce", utc=False)
    out["lat"] = pd.to_numeric(out["lat"], errors="coerce")
    out["lon"] = pd.to_numeric(out["lon"], errors="coerce")
    out["value"] = pd.to_numeric(out["value"], errors="coerce")

    for col in ["location_id", "variable", "source", "method"]:
        out[col] = out[col].astype("string")

    return out


def build_metadata(
    ds: xr.Dataset,
    variable: str,
    method: str,
    extra: dict | None = None,
) -> dict:
    """
    Pull the most important metadata out of the satellite dataset.

    We deliberately keep this block short - just the things a human needs
    to interpret the numbers correctly.

    Returns
    -------
    dict with keys:
        product_name, variable, units, description,
        spatial_resolution, time_coverage_start, time_coverage_end,
        extraction_method, generated_at
    """
    var_attrs = ds[variable].attrs if variable in ds.data_vars else {}
    file_attrs = ds.attrs

    meta = {
        "product_name": file_attrs.get("product_name", "unknown"),
        "variable": variable,
        "units": var_attrs.get("units", "unknown"),
        "description": var_attrs.get("long_name") or var_attrs.get("description", ""),
        "spatial_resolution": file_attrs.get("spatial_resolution", "unknown"),
        "time_coverage_start": str(file_attrs.get("time_coverage_start", "")),
        "time_coverage_end": str(file_attrs.get("time_coverage_end", "")),
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

    Parameters
    ----------
    df : DataFrame
        Already in canonical form (output of ``to_canonical``).
    output_csv : str or Path
        Where to write the CSV.
    metadata : dict, optional
        If provided, written next to the CSV as a ``.meta.txt`` file.

    Returns
    -------
    Path to the CSV that was written.
    """
    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    df_to_save = to_canonical(df)
    df_to_save.to_csv(output_csv, index=False)

    if metadata:
        meta_path = output_csv.with_suffix(".meta.txt")
        with meta_path.open("w", encoding="utf-8") as f:
            f.write("# Satellite extraction - metadata block\n")
            f.write(f"# Companion file for: {output_csv.name}\n")
            f.write("#\n")
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")

    return output_csv


def write_canonical_output(
    extracted_df: pd.DataFrame,
    ds: xr.Dataset,
    variable: str,
    method: str,
    output_csv: str | Path,
) -> Path:
    """
    One-liner: tidy up the extracted DataFrame, build metadata from the
    dataset, save both files.

    This is the function you usually call at the end of a pipeline.
    """
    metadata = build_metadata(ds=ds, variable=variable, method=method)
    return save_table(extracted_df, output_csv=output_csv, metadata=metadata)
