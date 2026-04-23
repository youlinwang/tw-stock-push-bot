"""Upload an image to a public HTTPS host for LINE image messages.

Two backends:
  - 0x0.st (no-auth, fast)                    — default
  - GitHub raw (commit + push to user's repo) — opt-in via `backend="github"`

0x0.st retains files for varying periods based on size (smaller files last longer;
up to ~365 days). Good for ephemeral daily push cards.
"""
from __future__ import annotations

import mimetypes
import subprocess
import urllib.request
import urllib.error
import uuid
from pathlib import Path


def _multipart(fields: dict[str, tuple[str, bytes, str]]) -> tuple[bytes, str]:
    boundary = "----" + uuid.uuid4().hex
    parts: list[bytes] = []
    for name, (filename, data, content_type) in fields.items():
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode()
        )
        parts.append(f"Content-Type: {content_type}\r\n\r\n".encode())
        parts.append(data)
        parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def upload_0x0(png_path: Path) -> str:
    data = png_path.read_bytes()
    content_type = mimetypes.guess_type(str(png_path))[0] or "image/png"
    body, ct_header = _multipart({"file": (png_path.name, data, content_type)})
    req = urllib.request.Request(
        "https://0x0.st",
        data=body,
        headers={
            "Content-Type": ct_header,
            "User-Agent": "tw-stock-bot/0.1 (tw-stock daily push)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            url = r.read().decode("utf-8").strip()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"0x0.st upload failed ({e.code}): {e.read().decode()[:200]}")
    if not url.startswith("https://"):
        raise RuntimeError(f"0x0.st returned unexpected body: {url[:200]}")
    return url


def upload_github(png_path: Path, repo_relpath: str = None) -> str:
    """Commit + push to origin main, return raw.githubusercontent.com URL.

    Requires git to be configured with push credentials. `png_path` must be
    inside the repo working tree.
    """
    repo_root = Path(__file__).resolve().parent
    rel = png_path.resolve().relative_to(repo_root)
    relpath = str(rel).replace("\\", "/")

    def sh(*args):
        return subprocess.run(args, cwd=repo_root, check=True, capture_output=True, text=True)

    sh("git", "add", relpath)
    sh("git", "commit", "-m", f"push image: {relpath}")
    sh("git", "push", "origin", "HEAD:main")
    # resolve current branch on origin
    remote_branch = "main"
    return f"https://raw.githubusercontent.com/youlinwang/tw-stock-push-bot/{remote_branch}/{relpath}"


def upload(png_path: Path, backend: str = "0x0") -> str:
    if backend == "0x0":
        return upload_0x0(png_path)
    if backend == "github":
        return upload_github(png_path)
    raise ValueError(f"unknown backend: {backend}")


if __name__ == "__main__":
    import sys
    backend = sys.argv[2] if len(sys.argv) > 2 else "0x0"
    print(upload(Path(sys.argv[1]), backend=backend))
