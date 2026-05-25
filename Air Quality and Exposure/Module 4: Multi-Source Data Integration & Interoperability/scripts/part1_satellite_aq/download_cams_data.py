from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Settings  (change these if you want a different month or area)
# ---------------------------------------------------------------------------
OUTPUT_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "cams_pm25_croatia.nc"

# We use the CAMS European AQ REANALYSES dataset, which provides truly
# hourly assimilated composition data (24 timestamps/day x 30 days for
# June 2024 = 720 timestamps).  This matches ERA5's hourly cadence so the
# two can be joined cleanly on (time, location_id).
#
# Time coverage:
#   - "validated_reanalysis" -> 2013 to ~12-18 months ago (final product)
#   - "interim_reanalysis"   -> overlaps and extends past validated by a
#                               few months (less polished, but recent)
#
# For 2024-06 we use the interim reanalysis.
YEAR = "2024"
MONTH = "06"
REANALYSIS_TYPE = "interim_reanalysis"

# Bounding box: [North, West, South, East] in decimal degrees.
# This one covers Croatia.
AREA = [47, 13, 42, 20]


def main() -> int:
    try:
        import cdsapi
    except ImportError:
        print(
            "ERROR: the 'cdsapi' package is not installed.\n"
            "       Run:  pip install cdsapi\n"
            "Then re-run this script.",
            file=sys.stderr,
        )
        return 1

    rc_path = Path.home() / ".cdsapirc"
    if not rc_path.exists():
        print(
            "ERROR: no API key file found at:\n"
            f"       {rc_path}\n\n"
            "Create it with these two lines (replace the token):\n\n"
            "    url: https://ads.atmosphere.copernicus.eu/api\n"
            "    key: <YOUR-PERSONAL-ACCESS-TOKEN>\n\n"
            "Get the token from https://ads.atmosphere.copernicus.eu/\n"
            "  (log in -> 'Your profile' -> 'Personal Access Token').\n"
            "Also accept the licence at:\n"
            "  https://ads.atmosphere.copernicus.eu/datasets/cams-europe-air-quality-reanalyses\n",
            file=sys.stderr,
        )
        return 2

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    dataset = "cams-europe-air-quality-reanalyses"
    request = {
        "variable": ["particulate_matter_2.5um"],
        "model": ["ensemble"],
        "level": ["0"],                       # 0 = surface
        "type": [REANALYSIS_TYPE],
        "year": [YEAR],
        "month": [MONTH],
        "data_format": "netcdf",
        "area": AREA,                         # [N, W, S, E]
    }

    print(f"Sending request to ADS for dataset: {dataset}")
    print("  variable:   pm2.5 (surface)")
    print(f"  period:     {YEAR}-{MONTH}  (full month, hourly)")
    print(f"  type:       {REANALYSIS_TYPE}")
    print(f"  area:       N={AREA[0]}, W={AREA[1]}, S={AREA[2]}, E={AREA[3]}")
    print()
    print("ADS may queue your request.  Progress will be printed below.")
    print("-" * 60)

    client = cdsapi.Client()
    client.retrieve(dataset, request, str(OUTPUT_PATH))

    size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print("-" * 60)
    print(f"DONE. Downloaded {size_mb:.2f} MB to:  {OUTPUT_PATH}")
    print()
    print("Next step: open notebooks/part1_satellite_aq/satellite_reader.ipynb")
    print("           and run all cells.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
