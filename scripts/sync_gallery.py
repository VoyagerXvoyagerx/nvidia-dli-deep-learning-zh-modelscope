#!/usr/bin/env python3
"""Publish course files to the existing Gallery using its web HTTP API.

The public /openapi/v1/galleries endpoint only creates Galleries; updating an
existing Gallery currently requires /api/v1/gallery and its draft/publish APIs.
Credentials come exclusively from MODELSCOPE_API_TOKEN, never repository files.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import time
from urllib.parse import urlsplit

import requests

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://modelscope.cn"
GALLERY_ID = "cb1503c2-1458-4f67-b9c3-bd505091cb47"
GALLERY_URL = BASE + "/gallery/VoyagerX/nvidia-dli-deep-learning-zh-modelscope"
ROOT_FILES = {"LICENSE", "README.md", "index.ipynb", "build_html.py"}
EXCLUDED_DIRS = {"environment", "slides", "__pycache__", ".ipynb_checkpoints", "tutorial_assets"}
MAX_FILES = 50


class SyncError(RuntimeError):
    pass


def selected(path: str) -> bool:
    parts = PurePosixPath(path).parts
    if not parts or any(part in {"..", "."} for part in parts) or path.startswith("/"):
        return False
    if path in ROOT_FILES:
        return True
    if parts[0] not in {"LICENSES", "course_content"}:
        return False
    return not any(part in EXCLUDED_DIRS or part.startswith(".") for part in parts) and parts[-1] != "model.pth"


def manifest(root: Path) -> list[str]:
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
    # Include newly generated HTML too; no generated commit or workflow loop needed.
    html_dir = root / "course_content/html"
    generated = [p.relative_to(root).as_posix() for p in html_dir.rglob("*") if p.is_file()]
    paths = sorted({p for p in tracked + generated if selected(p) and (root / p).is_file()})
    if not ROOT_FILES.issubset(paths) or not any(p.endswith(".ipynb") and p.startswith("course_content/tutorials/") for p in paths):
        raise SyncError("Course entry, root files or tutorial notebooks are missing")
    if len(paths) > MAX_FILES:
        raise SyncError(f"Gallery allows at most {MAX_FILES} files; selected {len(paths)}. Adjust the course file selection first.")
    for name in paths:
        p = root / name
        if p.is_symlink() or not p.resolve().is_relative_to(root.resolve()):
            raise SyncError(f"Unsupported symlink/path: {name}")
        if p.stat().st_size > 5 * 1024 * 1024:
            raise SyncError(f"File exceeds 5 MiB: {name}")
        if p.suffix == ".ipynb":
            nb = json.loads(p.read_text())
            if not any("".join(c.get("source", [])).strip() for c in nb.get("cells", [])):
                raise SyncError(f"Notebook has no content: {name}")
    return paths


class GalleryClient:
    def __init__(self, token: str, gid: str):
        self.gid = gid
        self.session = requests.Session()
        self.session.headers["Authorization"] = "Bearer " + token
        # ModelScope's legacy Gallery API uses m_session_id for owner permissions.
        self.session.cookies.set("m_session_id", token, domain="modelscope.cn", path="/")

    def api(self, method: str, path: str, **kwargs):
        try:
            response = self.session.request(method, BASE + path, timeout=(15, 180), **kwargs)
            if not response.ok:
                raise SyncError(f"Gallery {method} {path}: HTTP {response.status_code}")
            body = response.json()
        except (requests.RequestException, ValueError) as exc:
            # Do not log exception text: it may contain credentials or signed URLs.
            raise SyncError(f"Gallery {method} {path}: {type(exc).__name__}") from None
        if body.get("Success") is False or str(body.get("Code", 200)) != "200":
            raise SyncError(f"Gallery {method} {path}: API error code {body.get('Code')}")
        if "Data" not in body:
            raise SyncError(f"Gallery {method} {path}: missing Data")
        return body["Data"]

    def gallery(self):
        return self.api("GET", "/api/v1/gallery", params={"Gid": self.gid})["Gallery"]

    def upload_urls(self, names):
        data = self.api("POST", "/api/v1/gallery/square/files/upload", json={"Gid": self.gid, "FileNames": names})
        urls = {item["Filename"]: item.get("Url", "") for item in data["Urls"]}
        if set(urls) != set(names) or any(urlsplit(u).scheme != "https" or not urlsplit(u).hostname for u in urls.values()):
            raise SyncError("Upload API returned missing or invalid upload URLs")
        return urls

    def upload(self, root, name, url):
        for attempt in range(3):
            try:
                # A separate request prevents the ModelScope credential being sent to OSS.
                response = requests.put(url, data=(root / name).read_bytes(), headers={
                    "Content-Type": "application/octet-stream", "x-oss-meta-author": "aliy",
                }, timeout=(15, 180), allow_redirects=False)
                if response.ok:
                    print(f"Uploaded: {name}", flush=True)
                    return
                status = response.status_code
                if status not in {403, 408, 429, 500, 502, 503, 504}:
                    raise SyncError(f"Upload failed: {name}, HTTP {status}")
            except requests.RequestException:
                status = "network error"
            if attempt < 2:
                time.sleep(2 ** attempt)
                # Refresh expiring signed URLs before retrying the idempotent PUT.
                url = self.upload_urls([name])[name]
        raise SyncError(f"Upload failed after retries: {name}, {status}")


def fingerprint(gallery):
    # Abort if a person changes published content/metadata during the upload.
    keys = ("Name", "Owner", "Path", "Category", "EntryFile", "Files", "Label", "Private", "GmtUpdated")
    return {key: gallery.get(key) for key in keys}


def publish(client, root, paths):
    original = client.gallery()
    if original.get("Owner") != "VoyagerX" or original.get("Role") != "admin":
        raise SyncError("Token must have admin access to the VoyagerX Gallery")
    entry = original.get("EntryFile", "")
    category = original.get("Category")
    suffixes = {"notebook": ".ipynb", "website": ".html", "pdf": ".pdf", "file": None}
    if entry not in paths or category not in suffixes or (suffixes[category] and Path(entry).suffix.lower() != suffixes[category]):
        raise SyncError("Current Gallery entry/category is incompatible with the selected files; refusing to change it")
    # Request URLs in small batches and use them immediately, before they expire.
    for start in range(0, len(paths), 6):
        batch = paths[start:start + 6]
        urls = client.upload_urls(batch)
        with ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(lambda name: client.upload(root, name, urls[name]), batch))
    draft = client.api("GET", "/api/v1/gallery/square/files", params={"Gid": client.gid, "Draft": True})
    sizes = {f["FileName"]: f.get("Size") for f in draft["Files"]}
    if any(sizes.get(name) != (root / name).stat().st_size for name in paths):
        raise SyncError("Draft is incomplete or has incorrect file sizes; publication aborted")
    if fingerprint(client.gallery()) != fingerprint(original):
        raise SyncError("Gallery changed during upload; publication aborted. Run the workflow again.")
    client.api("PUT", "/api/v1/gallery", json={
        "Gid": client.gid, "Name": original["Name"], "Owner": original["Owner"],
        "Category": original["Category"], "EntryFile": original["EntryFile"],
        "Files": json.dumps(paths, ensure_ascii=False),
        "Label": json.dumps(original.get("Label", []), ensure_ascii=False),
        "Private": 0, "Action": "open",
    })
    client.api("PUT", "/api/v1/gallery/publish", json={"Gid": client.gid})
    result = client.gallery()
    if set(result["Files"]) != set(paths) or result.get("Private") not in (False, 0) or result.get("EntryFile") != entry or result.get("Category") != category:
        raise SyncError("Published Gallery metadata does not match the expected course")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Validate/list files without network calls or credentials")
    args = parser.parse_args()
    paths = manifest(ROOT)
    print(f"Gallery manifest: {len(paths)}/{MAX_FILES} files")
    if args.dry_run:
        print("\n".join(paths))
        return
    token = os.environ.get("MODELSCOPE_API_TOKEN", "").strip()
    if not token:
        raise SyncError("Set the MODELSCOPE_API_TOKEN repository Actions Secret")
    result = publish(GalleryClient(token, os.environ.get("MODELSCOPE_GALLERY_ID", GALLERY_ID)), ROOT, paths)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    pending = result.get("CsiPending", [])
    summary = f"Published {len(paths)} files from commit `{commit}` to [ModelScope Gallery]({GALLERY_URL}).\n"
    if pending:
        summary += "\nFiles awaiting ModelScope content review (download URLs may temporarily be empty):\n" + "\n".join(f"- `{p}`" for p in pending) + "\n"
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as out:
            out.write(summary)


if __name__ == "__main__":
    try:
        main()
    except SyncError as exc:
        print(f"Gallery sync failed: {exc}", file=sys.stderr)
        sys.exit(1)
