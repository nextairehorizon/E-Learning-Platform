from __future__ import annotations

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Synthetic auxiliary data factories
# ---------------------------------------------------------------------------
#
# These produce realistic hourly traffic, station-meteo, and static-context
# tables for the Part 5 teaching notebook.  Real ingestion adapters (CSV
# readers + column renames) live downstream in the partner pipeline.


def synth_traffic(
    stations: pd.DataFrame,
    *,
    start: str = "2024-06-01",
    end: str = "2024-06-30 23:00",
    freq: str = "1h",
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    """
    Generate a realistic hourly traffic-counter dataset for the given
    stations.

    One counter per station, identified by ``location_id``.  Volumes
    follow a weekday/weekend split and a morning + evening rush-hour
    pattern.  Heavy-vehicle share is higher off-peak.
    """
    rng = rng or np.random.default_rng(7)
    times = pd.date_range(start=start, end=end, freq=freq)

    pieces: list[pd.DataFrame] = []
    for _, st in stations.iterrows():
        is_weekend = times.weekday >= 5
        hour = times.hour
        morning = np.exp(-((hour - 8) / 2.0) ** 2)
        evening = np.exp(-((hour - 18) / 2.0) ** 2)
        base = 80 + 700 * (morning + evening)
        base = np.where(is_weekend, 0.55 * base, base)
        noise = rng.normal(0, 35, size=len(times))
        counts = np.clip(base + noise, 5, None).astype(int)

        speed = np.clip(
            65 - 0.04 * counts + rng.normal(0, 3, size=len(times)),
            10, 90,
        )
        heavy = np.clip(
            0.08 + 0.05 * (1 - (morning + evening)) + rng.normal(0, 0.02, size=len(times)),
            0.0, 0.4,
        )

        pieces.append(pd.DataFrame({
            "counter_id": f"CTR_{st['location_id']}",
            "time": times,
            "vehicle_count": counts,
            "speed_kmh": speed,
            "heavy_fraction": heavy,
            "location_id": st["location_id"],
        }))

    return pd.concat(pieces, ignore_index=True)


def synth_station_meteo(
    stations: pd.DataFrame,
    *,
    start: str = "2024-06-01",
    end: str = "2024-06-30 23:00",
    freq: str = "1h",
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    """Generate a realistic hourly station-meteo dataset for the registry."""
    rng = rng or np.random.default_rng(11)
    times = pd.date_range(start=start, end=end, freq=freq)
    hour = times.hour
    diurnal = 6.0 * np.sin((hour - 4) / 24.0 * 2 * np.pi)

    pieces: list[pd.DataFrame] = []
    for _, st in stations.iterrows():
        lat_factor = 22.0 - 0.4 * (st["lat"] - 43.0)  # cooler further north
        temp = lat_factor + diurnal + rng.normal(0, 0.8, size=len(times))
        rh = np.clip(60 - 0.7 * diurnal + rng.normal(0, 5, size=len(times)), 15, 100)
        wind = np.clip(2.0 + rng.gamma(2.0, 0.8, size=len(times)), 0.1, 18)
        wind_dir = rng.uniform(0, 360, size=len(times))
        pres = 1013.0 + rng.normal(0, 3, size=len(times))

        pieces.append(pd.DataFrame({
            "location_id": st["location_id"],
            "time": times,
            "temperature_c": temp,
            "humidity_pct": rh,
            "wind_speed_ms": wind,
            "wind_dir_deg": wind_dir,
            "pressure_hpa": pres,
        }))

    return pd.concat(pieces, ignore_index=True)


def synth_static_context(
    stations: pd.DataFrame,
    *,
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    """Generate a static-context table (elevation, road distance, ...)."""
    rng = rng or np.random.default_rng(23)
    n = len(stations)
    return pd.DataFrame({
        "location_id": stations["location_id"].values,
        "elevation_m": rng.uniform(5, 350, size=n).round(1),
        "land_use_code": rng.choice([11100, 12100, 14100, 21000, 31000], size=n),
        "lcz_class": rng.choice([2, 3, 5, 6, 8, 14], size=n),
        "road_dist_m": rng.uniform(20, 500, size=n).round(1),
        "energy_intensity_kwh_m2": rng.uniform(60, 220, size=n).round(1),
    })
