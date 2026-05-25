from __future__ import annotations

import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Settings  (change these to fetch a different day or area)
# ---------------------------------------------------------------------------
OUTPUT_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "era5_meteo_croatia.nc"

# Match the CAMS file from Part 1 so the two datasets are comparable.
# A full month gives Part 3 (temporal harmonisation) enough data to show
# diurnal/weekly cycles and meaningful coverage diagnostics.
YEAR = "2024"
MONTH = "06"
DAYS = [f"{d:02d}" for d in range(1, 31)]  # June has 30 days

# Bounding box: [North, West, South, East] in decimal degrees.
AREA = [47, 13, 42, 20]

# ERA5 is hourly, and we want every hour: 24 timestamps per day x 30 days
# = 720 timestamps in total.  The hourly density is what lets Part 3
# demonstrate intersecting a dense reanalysis axis onto the sparser
# 6-hourly CAMS analysis axis.
HOURS = [f"{h:02d}:00" for h in range(24)]

# A compact, AQ-relevant subset of ERA5 single-level fields:
#   - 2m temperature / dewpoint  -> humidity proxies
#   - 10m u/v wind components    -> dispersion
#   - surface pressure           -> baseline state
#   - boundary layer height      -> dilution volume (very useful for PM)
#   - total precipitation        -> wet deposition / wash-out
VARIABLES = [
    "2m_temperature",
    "2m_dewpoint_temperature",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "surface_pressure",
    "boundary_layer_height",
    "total_precipitation",
]


# ---------------------------------------------------------------------------
# Credentials helper
# ---------------------------------------------------------------------------
#
# ERA5 lives on the *Climate* Data Store (CDS), which is a different service
# from the CAMS Atmosphere Data Store (ADS) used in Part 1.  Each one has its
# own URL and its own personal access token.
#
# This script accepts credentials from two places, in order:
#   1. Environment variables  CDSAPI_URL  and  CDSAPI_KEY
#   2. The file               ~/.cdsapirc
#
# Recommended setup if you also have an ADS token for Part 1:
#   - leave ~/.cdsapirc pointing at ADS,
#   - set CDSAPI_URL / CDSAPI_KEY for CDS in the terminal where you run
#     this script.
#
CDS_URL = "https://cds.climate.copernicus.eu/api"


def _read_credentials() -> tuple[str | None, str | None]:
    url = os.environ.get("CDSAPI_URL")
    key = os.environ.get("CDSAPI_KEY")
    if url and key:
        return url, key

    rc_path = Path.home() / ".cdsapirc_ERA5"
    if not rc_path.exists():
        return None, None

    config: dict[str, str] = {}
    for line in rc_path.read_text(encoding="utf-8").splitlines():
        if ":" in line and not line.strip().startswith("#"):
            k, _, v = line.partition(":")
            config[k.strip()] = v.strip()
    return config.get("url"), config.get("key")


def _print_setup_instructions() -> None:
    print(
        "ERROR: no CDS (Climate Data Store) credentials found.\n\n"
        "ERA5 is on the CDS, which is separate from the CAMS Atmosphere\n"
        "Data Store (ADS) used in Part 1.\n\n"
        "1. Create a free account at https://cds.climate.copernicus.eu/\n"
        "2. Copy your Personal Access Token (top right -> 'Your profile').\n"
        "3. Accept the dataset licence at\n"
        "   https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels\n"
        "4. Provide the credentials in one of two ways:\n\n"
        "   (a) Environment variables (recommended if you also use ADS):\n"
        "       setx CDSAPI_URL https://cds.climate.copernicus.eu/api\n"
        "       setx CDSAPI_KEY <YOUR-CDS-TOKEN>\n"
        "       (then open a new terminal)\n\n"
        "   (b) Or replace ~/.cdsapirc with:\n"
        "       url: https://cds.climate.copernicus.eu/api\n"
        "       key: <YOUR-CDS-TOKEN>\n",
        file=sys.stderr,
    )


def main() -> int:
    try:
        import cdsapi
    except ImportError:
        print(
            "ERROR: the 'cdsapi' package is not installed.\n"
            "       Run:  pip install cdsapi",
            file=sys.stderr,
        )
        return 1

    url, key = _read_credentials()
    if not url or not key:
        _print_setup_instructions()
        return 2

    if "cds.climate.copernicus.eu" not in url:
        print(
            "ERROR: the CDS URL looks wrong.\n"
            f"       Got:      {url}\n"
            f"       Expected: {CDS_URL}\n\n"
            "If your ~/.cdsapirc points at the ADS, set CDSAPI_URL and\n"
            "CDSAPI_KEY environment variables for this script instead.\n",
            file=sys.stderr,
        )
        return 3

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    dataset = "reanalysis-era5-single-levels"
    request = {
        "product_type": ["reanalysis"],
        "variable": VARIABLES,
        "year": [YEAR],
        "month": [MONTH],
        "day": DAYS,
        "time": HOURS,
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": AREA,
    }

    print(f"Sending request to CDS for dataset: {dataset}")
    print(f"  variables:  {len(VARIABLES)} fields (meteo)")
    for v in VARIABLES:
        print(f"              - {v}")
    print(
        f"  date:       {YEAR}-{MONTH}-{DAYS[0]} to {YEAR}-{MONTH}-{DAYS[-1]}  "
        f"({len(DAYS) * len(HOURS)} hourly steps)"
    )
    print(f"  area:       N={AREA[0]}, W={AREA[1]}, S={AREA[2]}, E={AREA[3]}")
    print()
    print("CDS may queue your request.  Progress will be printed below.")
    print("-" * 60)

    client = cdsapi.Client(url=url, key=key)
    client.retrieve(dataset, request, str(OUTPUT_PATH))

    size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print("-" * 60)
    print(f"DONE. Downloaded {size_mb:.2f} MB to:  {OUTPUT_PATH}")
    print()
    print("Next step: open notebooks/reanalysis_reader.ipynb and run all cells.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
