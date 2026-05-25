from __future__ import annotations

import argparse
import io
import sys
import zipfile
from pathlib import Path


DEFAULT_DATA_DIR = Path(__file__).parent.parent.parent / "data"


def _print_instructions(out_dir: Path) -> None:
    print(
        "\n"
        "========================================================\n"
        "  How to download the Urban Atlas ZIP via browser\n"
        "========================================================\n"
        "\n"
        "1. Log in at:\n"
        "   https://land.copernicus.eu/en/user-corner/my-account\n"
        "\n"
        "2. Go to the dataset page:\n"
        "   https://land.copernicus.eu/en/products/urban-atlas/urban-atlas-2018\n"
        "\n"
        "3. Click  Download  and select the Zagreb FGB file (~112 MB).\n"
        "\n"
        "4. Wait for the e-mail confirmation, then download the ZIP.\n"
        "\n"
        "5. Run this script, pointing it at the downloaded file:\n"
        f"   python scripts/prepare_urban_atlas.py --zip PATH\\TO\\file.zip\n"
        f"   (extracted .fgb will be saved to: {out_dir})\n"
        "========================================================\n"
    )


def _stream_entry(zf: zipfile.ZipFile, entry_name: str, output_file: Path) -> None:
    """Stream *entry_name* from *zf* to *output_file* with progress."""
    with zf.open(entry_name) as src, open(output_file, "wb") as dst:
        chunk = src.read(1 << 20)
        total = 0
        while chunk:
            dst.write(chunk)
            total += len(chunk)
            print(f"\r  {total >> 20} MB written", end="", flush=True)
            chunk = src.read(1 << 20)
    print()


def extract_zip(zip_path: Path, out_dir: Path) -> None:
    """Extract the first .fgb from *zip_path* into *out_dir*.

    Handles one level of nesting: if the outer ZIP contains only another ZIP,
    that inner ZIP is opened in memory and its .fgb is extracted directly.
    """
    if not zip_path.exists():
        print(f"ERROR: ZIP not found: {zip_path}", file=sys.stderr)
        _print_instructions(out_dir)
        raise SystemExit(1)

    out_dir.mkdir(parents=True, exist_ok=True)
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"ZIP  : {zip_path}  ({size_mb:.1f} MB)")
    print(f"Output dir: {out_dir}")
    print("Extracting …")

    with zipfile.ZipFile(zip_path) as outer:
        contents = outer.namelist()
        fgb_entries = [n for n in contents if n.lower().endswith(".fgb")]

        if fgb_entries:
            fgb_name = fgb_entries[0]
            print(f"  Found: {fgb_name}")
            output_file = out_dir / Path(fgb_name).name
            _stream_entry(outer, fgb_name, output_file)

        else:
            inner_zips = [n for n in contents if n.lower().endswith(".zip")]
            if not inner_zips:
                print("Contents of ZIP:")
                for name in contents:
                    print(f"  {name}")
                print("\nERROR: No .fgb or inner .zip found inside the ZIP.", file=sys.stderr)
                raise SystemExit(1)

            inner_name = inner_zips[0]
            print(f"  Outer ZIP contains inner ZIP: {inner_name}")
            inner_bytes = outer.read(inner_name)
            with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
                inner_contents = inner.namelist()
                fgb_entries = [n for n in inner_contents if n.lower().endswith(".fgb")]
                if not fgb_entries:
                    print("Contents of inner ZIP:")
                    for name in inner_contents:
                        print(f"  {name}")
                    print("\nERROR: No .fgb found inside the inner ZIP.", file=sys.stderr)
                    raise SystemExit(1)

                fgb_name = fgb_entries[0]
                print(f"  Found (in inner ZIP): {fgb_name}")
                output_file = out_dir / Path(fgb_name).name
                _stream_entry(inner, fgb_name, output_file)

    out_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"\nDone!  FGB ready at:\n  {output_file}  ({out_mb:.0f} MB)")
    print("\nYou can now run the notebook Section 12 to visualise the data.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract the Urban Atlas FGB from a manually downloaded ZIP.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--zip",
        metavar="PATH",
        default=None,
        help=(
            "Path to the downloaded ZIP file. "
            "If omitted, the script looks for the first *.zip in the output directory."
        ),
    )
    parser.add_argument(
        "--out",
        metavar="DIR",
        default=str(DEFAULT_DATA_DIR),
        help=f"Directory where the .fgb will be saved (default: {DEFAULT_DATA_DIR})",
    )
    args = parser.parse_args()

    out_dir = Path(args.out).expanduser().resolve()

    if args.zip:
        zip_path = Path(args.zip).expanduser().resolve()
    else:
        candidates = sorted(out_dir.glob("*.zip"))
        if not candidates:
            print("No ZIP file found. Pass --zip PATH to specify one.")
            _print_instructions(out_dir)
            raise SystemExit(1)
        zip_path = candidates[0]
        if len(candidates) > 1:
            print(f"Multiple ZIPs found; using: {zip_path.name}")
            print("Pass --zip to choose a specific file.")

    expected_fgb = out_dir / (zip_path.stem + ".fgb")
    if expected_fgb.exists():
        size_mb = expected_fgb.stat().st_size / (1024 * 1024)
        print(f"FGB already present ({size_mb:.0f} MB):\n  {expected_fgb}")
        print("Delete it to re-extract.")
        return

    extract_zip(zip_path, out_dir)


if __name__ == "__main__":
    main()
