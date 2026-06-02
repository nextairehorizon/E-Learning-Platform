from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

import xarray as xr


_DEFAULT_ENGINES = ("netcdf4", "h5netcdf")


def _load_data(
    zip_path: str | Path,
    *,
    engine: str | None = None,
) -> xr.Dataset:
    """Open a CDS ZIP bundle and merge every inner NetCDF into one Dataset.

    Parameters
    ----------
    zip_path : str or Path
        Path to the ZIP file delivered by CDS / ADS.
    engine : str, optional
        Force a specific xarray backend (``"netcdf4"`` or ``"h5netcdf"``).
        If ``None`` (default) each inner file is opened with the first
        engine in :data:`_DEFAULT_ENGINES` that works — so the same
        helper handles both CAMS PM2.5 and ERA5 bundles transparently.

    Returns
    -------
    xarray.Dataset
        Eagerly-loaded merge of every inner NetCDF.  Temporary files
        used during the read are removed before returning.
    """
    zip_path = Path(zip_path)
    candidates = (engine,) if engine else _DEFAULT_ENGINES

    datasets: list[xr.Dataset] = []
    tmp_paths: list[str] = []

    try:
        with zipfile.ZipFile(zip_path) as z:
            for name in z.namelist():
                tmp = tempfile.NamedTemporaryFile(suffix=".nc", delete=False)
                tmp.write(z.read(name))
                tmp.close()
                tmp_paths.append(tmp.name)

                last_err: Exception | None = None
                for eng in candidates:
                    try:
                        ds = xr.open_dataset(tmp.name, engine=eng)
                        ds.load()  # read into memory before the temp file vanishes
                        datasets.append(ds)
                        last_err = None
                        break
                    except Exception as e:
                        last_err = e
                if last_err is not None:
                    raise RuntimeError(
                        f"Could not open inner file {name!r} from {zip_path} "
                        f"with engines {candidates}: {last_err}"
                    ) from last_err

        return xr.merge(datasets)
    finally:
        for ds in datasets:
            ds.close()
        for path in tmp_paths:
            try:
                Path(path).unlink()
            except OSError:
                pass
