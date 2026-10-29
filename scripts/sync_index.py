#!/usr/bin/env python3
"""Generate the Gallery welcome notebook from README, retaining tracking URLs."""
from __future__ import annotations

import html
import json
from pathlib import Path
import re
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
GITHUB = "https://github.com/VoyagerXvoyagerx/nvidia-dli-deep-learning-zh-modelscope"
GALLERY = "https://modelscope.cn/gallery/NVIDIA_Training_and_Certification/nvidia-dli-deep-learning-zh-modelscope"


def entry_markdown(readme: str) -> str:
    # Notebook/HTML do not require a Mermaid runtime: show the same learning order as a list.
    def learning_path(match):
        nodes = re.findall(r'^\s*\w+\["<b>([^<]+)</b><br/>(.*?)"\]', match.group(1), re.M)
        if not nodes:
            return match.group(0)
        return "\n".join(
            f"{i}. [{name}](course_content/tutorials/{name}.ipynb) · "
            + html.unescape(re.sub(r"<[^>]+>", " · ", label))
            for i, (name, label) in enumerate(nodes, 1)
        ) + "\n"

    markdown = re.sub(r"```mermaid\n(.*?)\n```", learning_path, readme, flags=re.S)

    def asset_link(match):
        label, relative = match.groups()
        relative = relative.removeprefix("./")
        base = GITHUB + "/raw/refs/heads/main/" if relative.lower().endswith((".ppt", ".pptx")) else GALLERY + "/files/"
        return f"[{label}]({base}{quote(relative, safe='/')})"

    # Only project-relative asset links change; external URLs and ncid parameters are copied verbatim.
    return re.sub(r"\[([^\]]+)\]\(((?:\./)?course_content/[^)]+)\)", asset_link, markdown)


def sync_index():
    path = ROOT / "index.ipynb"
    notebook = json.loads(path.read_text(encoding="utf-8"))
    notebook["cells"][0]["source"] = entry_markdown((ROOT / "README.md").read_text(encoding="utf-8")).splitlines(keepends=True)
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("Updated index.ipynb from README.md (external tracking URLs preserved)")


if __name__ == "__main__":
    sync_index()
