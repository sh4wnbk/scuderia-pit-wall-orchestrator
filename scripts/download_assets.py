"""
Container startup script — downloads chroma_db/ and fastf1_cache/ from Dropbox.
Runs before uvicorn starts. Gracefully skips if DROPBOX_TOKEN is not set,
leaving any bundled assets intact.

Called by Dockerfile CMD:
    python scripts/download_assets.py && uvicorn app:app ...
"""

import io
import os
import zipfile

ASSETS = [
    ("/chroma_db.zip",    "./chroma_db"),
    ("/fastf1_cache.zip", "./fastf1_cache"),
]


def main():
    token = os.getenv("DROPBOX_TOKEN")
    if not token:
        print("[Assets] DROPBOX_TOKEN not set — using bundled assets")
        return

    try:
        import dropbox
    except ImportError:
        print("[Assets] dropbox package not installed — using bundled assets")
        return

    dbx = dropbox.Dropbox(token)

    for remote_path, local_dir in ASSETS:
        # Skip if directory already has content (e.g. cached layer)
        if os.path.isdir(local_dir) and len(os.listdir(local_dir)) > 1:
            print(f"[Assets] {local_dir} already present — skipping")
            continue
        try:
            print(f"[Assets] Downloading {remote_path} from Dropbox...")
            _, res = dbx.files_download(remote_path)
            with zipfile.ZipFile(io.BytesIO(res.content)) as zf:
                zf.extractall(".")
            print(f"[Assets] {local_dir} restored ({len(res.content) / 1024 / 1024:.1f} MB)")
        except dropbox.exceptions.ApiError as e:
            print(f"[Assets] {remote_path} not found in Dropbox — using bundled: {e}")
        except Exception as e:
            print(f"[Assets] Download failed for {remote_path} — using bundled: {e}")

    print("[Assets] Done")


if __name__ == "__main__":
    main()
