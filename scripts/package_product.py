#!/usr/bin/env python3
"""package_product.py - Create a clean production zip bundle of kilo-bridge-setup."""
import os
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {
    ".git",
    "venv",
    ".runtime",
    "__pycache__",
    "node_modules",
    "temp",
    "_backup-fix",
}

EXCLUDE_EXTENSIONS = {".pyc", ".pyo"}

EXCLUDE_FILENAMES = {
    "daemon.log",
}


def should_include(rel_path: Path) -> bool:
    for part in rel_path.parts:
        if part in EXCLUDE_DIRS:
            return False
    if rel_path.suffix in EXCLUDE_EXTENSIONS:
        return False
    if rel_path.name in EXCLUDE_FILENAMES:
        return False
    if rel_path.name.startswith("_drive_test_") and rel_path.name.endswith(".log"):
        return False
    if rel_path.name.endswith(".previous"):
        return False
    return True


def make_zip(out_zip: Path):
    print(f"Creating package zip at: {out_zip}")
    file_count = 0
    total_uncompressed = 0

    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for file_path in ROOT.rglob("*"):
            if file_path.is_file():
                rel = file_path.relative_to(ROOT)
                if should_include(rel):
                    archive_name = Path("kilo-bridge-setup") / rel
                    zf.write(file_path, str(archive_name))
                    file_count += 1
                    total_uncompressed += file_path.stat().st_size

    size_mb = out_zip.stat().st_size / (1024 * 1024)
    uncomp_mb = total_uncompressed / (1024 * 1024)
    print(f"[OK] Packaged {file_count} files into {out_zip}")
    print(f"     Uncompressed: {uncomp_mb:.2f} MB | Compressed: {size_mb:.2f} MB")
    return size_mb


if __name__ == "__main__":
    downloads_zip = Path(r"C:\Users\Admin\Downloads\kilo-bridge-setup.zip")
    onedrive_dir = Path(r"C:\Users\Admin\OneDrive")
    onedrive_zip = onedrive_dir / "kilo-bridge-setup.zip"

    # 1. Build zip in Downloads
    make_zip(downloads_zip)

    # 2. Copy to OneDrive for cloud sync
    if onedrive_dir.is_dir():
        shutil.copy2(downloads_zip, onedrive_zip)
        print(f"[OK] Uploaded/Copied to OneDrive: {onedrive_zip}")
    else:
        print("[WARN] OneDrive directory not found.")
