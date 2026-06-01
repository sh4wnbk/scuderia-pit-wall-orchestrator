"""
One-time upload of chroma_db/ and fastf1_cache/ to Dropbox.
Run locally after indexing or adding new FastF1 cache files.

Usage:
    source .ibm_scuderia/bin/activate
    python scripts/upload_assets.py

Requires DROPBOX_TOKEN in .env or environment.
"""

import io
import os
import sys
import zipfile
from pathlib import Path

import dropbox
from dotenv import load_dotenv

load_dotenv()

CHUNK_SIZE = 100 * 1024 * 1024  # 100 MB chunks for large file uploads

ASSETS = [
    ("chroma_db",     "/chroma_db.zip"),
    ("fastf1_cache",  "/fastf1_cache.zip"),
]


def zip_directory(local_dir: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(local_dir):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, start=".")
                zf.write(filepath, arcname)
    return buf.getvalue()


def upload(dbx: dropbox.Dropbox, data: bytes, remote_path: str) -> None:
    size = len(data)
    print(f"  Uploading {size / 1024 / 1024:.1f} MB → {remote_path}")

    if size <= CHUNK_SIZE:
        dbx.files_upload(data, remote_path, mode=dropbox.files.WriteMode.overwrite)
    else:
        # Chunked upload for large files
        session = dbx.files_upload_session_start(data[:CHUNK_SIZE])
        cursor = dropbox.files.UploadSessionCursor(
            session_id=session.session_id, offset=CHUNK_SIZE
        )
        offset = CHUNK_SIZE
        while offset < size:
            chunk = data[offset: offset + CHUNK_SIZE]
            remaining = size - (offset + len(chunk))
            if remaining == 0:
                commit = dropbox.files.CommitInfo(
                    path=remote_path,
                    mode=dropbox.files.WriteMode.overwrite,
                )
                dbx.files_upload_session_finish(chunk, cursor, commit)
            else:
                dbx.files_upload_session_append_v2(chunk, cursor)
                cursor.offset += len(chunk)
            offset += len(chunk)

    print(f"  Done → {remote_path}")


def main():
    token = os.getenv("DROPBOX_TOKEN")
    if not token:
        print("ERROR: DROPBOX_TOKEN not set in .env")
        sys.exit(1)

    dbx = dropbox.Dropbox(token)
    print(f"Connected to Dropbox app folder\n")

    for local_dir, remote_path in ASSETS:
        if not Path(local_dir).exists():
            print(f"SKIP: {local_dir} not found")
            continue
        print(f"Zipping {local_dir}/...")
        data = zip_directory(local_dir)
        upload(dbx, data, remote_path)

    print("\nAll assets uploaded.")
    print("Dropbox app folder now contains: chroma_db.zip, fastf1_cache.zip")


if __name__ == "__main__":
    main()
