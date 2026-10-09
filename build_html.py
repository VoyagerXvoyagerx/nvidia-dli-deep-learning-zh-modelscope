#!/usr/bin/env python3
"""Build a static, D2L-inspired course reader without executing notebooks.

Usage: python build_html.py
Dependencies: nbconvert, nbformat, beautifulsoup4 (included in the Notebook image).
"""
from __future__ import annotations

import argparse
import html
import json
import mimetypes
import re
from base64 import b64encode
from pathlib import Path
from urllib.parse import unquote, urlsplit

import nbformat
from bs4 import BeautifulSoup
from nbconvert import HTMLExporter
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent
GITHUB = "https://github.com/VoyagerXvoyagerx/nvidia-dli-deep-learning-zh-modelscope"
GALLERY = "https://modelscope.cn/gallery/VoyagerX/nvidia-dli-deep-learning-zh-modelscope"
TITLES = {
    "index": "前言与课程导航",
    "00_jupyterlab": "00 · JupyterLab 入门",
    "01_mnist": "01 · 深度学习简介与 MNIST",
    "02_asl": "02 · 神经网络训练与美国手语",
    "03_asl_cnn": "03 · 卷积神经网络",
    "04a_asl_augmentation": "04a · 数据增强",
    "04b_asl_predictions": "04b · 模型部署与预测",
    "05a_doggy_door": "05a · VGG16 预训练模型",
    "05b_corgi_door": "05b · 柯基识别与迁移学习",
    "06_nlp": "06 · BERT 与自然语言处理",
}

CSS = """
:root{--blue:#1976d2;--ink:#37474f;--muted:#697b86;--line:#e5ebef}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:82px}
body{margin:0;color:var(--ink);background:#fff;font:16px/1.85 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans SC","Microsoft YaHei",sans-serif}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}
.topbar{height:64px;position:fixed;inset:0 0 auto;background:var(--blue);color:white;display:flex;align-items:center;gap:25px;padding:0 30px;z-index:20;box-shadow:0 2px 6px #0002}
.brand{font-size:19px;font-weight:600;color:white;letter-spacing:.2px}.toplinks{margin-left:auto;display:flex;gap:22px}.toplinks a{color:white;font-size:14px}.menu{display:none;border:0;background:none;color:white;font-size:24px;cursor:pointer}
.sidebar{position:fixed;top:64px;bottom:0;width:280px;padding:30px 20px 40px;overflow:auto;border-right:1px solid var(--line);background:#fafcfd;z-index:15}
.sidebar h2,.toc h2{font-size:14px;margin:0 0 16px;color:var(--muted);font-weight:500}.search{width:100%;padding:10px 12px;border:1px solid #d7e0e5;border-radius:4px;background:white;font-size:14px;margin-bottom:22px}
.chapters{list-style:none;padding:0;margin:0}.chapters li{margin:3px 0}.chapters a{display:block;padding:8px 12px;border-radius:3px;font-size:14px;color:#455a64;line-height:1.65}.chapters a.active{background:#e3f2fd;color:var(--blue);font-weight:600;border-left:3px solid var(--blue)}
main{margin:64px 230px 0 280px;padding:38px 48px 55px;max-width:1140px;min-height:calc(100vh - 64px)}.breadcrumb{font-size:13px;color:var(--muted);margin-bottom:17px}.page-title{font-size:32px;line-height:1.4;font-weight:500;margin:0 0 12px}.subtitle{color:var(--muted);font-size:13px;border-bottom:1px solid var(--line);padding-bottom:23px;margin-bottom:25px}
.toc{position:fixed;right:0;top:94px;width:230px;padding:10px 24px;max-height:calc(100vh - 110px);overflow:auto;border-left:1px solid var(--line)}.toc a{display:block;font-size:12px;line-height:1.7;margin:9px 0;color:var(--muted)}.toc a.depth-3{padding-left:12px}
.notebook h1{font-size:28px}.notebook h2{font-size:24px}.notebook h3{font-size:20px}.notebook h4{font-size:17px}.notebook h1,.notebook h2,.notebook h3,.notebook h4{font-weight:500;line-height:1.5;margin:32px 0 15px}.notebook p{margin:12px 0}.notebook img{max-width:100%;height:auto}.notebook table{border-collapse:collapse;display:block;overflow-x:auto;max-width:100%;font-size:14px;margin:20px 0}.notebook th,.notebook td{border:1px solid #dfe6ea;padding:10px 13px;vertical-align:top}.notebook th{background:#f5f8fa}.notebook blockquote{border-left:4px solid #90caf9;background:#f4f9fd;padding:8px 20px;margin:20px 0}.notebook ul,.notebook ol{padding-left:25px}
code,pre{font:13px/1.65 ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace}p code,li code,td code{background:#f0f4f6;border-radius:3px;padding:2px 5px;color:#b33b56}.highlight{position:relative;background:#f6f8fa!important;border:1px solid #e1e8ec;border-radius:4px;margin:15px 0;overflow:auto}.highlight pre{margin:0;padding:16px 20px;overflow:auto;background:transparent;white-space:pre}.copy{position:absolute;right:7px;top:6px;border:1px solid #dce3e8;border-radius:3px;padding:3px 8px;background:white;font-size:11px;color:#607d8b;cursor:pointer;opacity:0}.highlight:hover .copy,.copy:focus{opacity:1}.output_area pre{white-space:pre-wrap;padding:12px 18px;background:#fbfcfd;border-left:3px solid #cfd8dc}.prompt,.anchor-link{display:none}.cell{margin:20px 0}.input_area{width:100%}.jp-RenderedHTMLCommon{overflow-wrap:anywhere}.text_cell_render{padding:0}.MathJax{max-width:100%;overflow-x:auto;overflow-y:hidden}
.pager{display:flex;justify-content:space-between;gap:20px;margin-top:50px;padding-top:24px;border-top:1px solid var(--line);font-size:14px}.footer{margin-top:35px;color:var(--muted);font-size:12px}.empty-search{font-size:13px;color:var(--muted);display:none}
@media(min-width:1800px){main{margin-left:calc(280px + (100vw - 1800px)/2)}}
@media(max-width:1200px){.toc{display:none}main{margin-right:0;padding:30px 35px}}@media(max-width:760px){.topbar{padding:0 16px;gap:12px}.brand{font-size:15px}.toplinks{gap:12px}.toplinks a{font-size:12px}.menu{display:block}.sidebar{display:none;width:280px;box-shadow:3px 0 9px #0002}.sidebar.open{display:block}main{margin:64px 0 0;padding:25px 20px}.page-title{font-size:25px}.notebook h2{font-size:21px}.copy{opacity:1}}
"""

JS = """
document.querySelector('.menu').addEventListener('click',()=>{const n=document.querySelector('.sidebar');n.classList.toggle('open');document.querySelector('.menu').setAttribute('aria-expanded',n.classList.contains('open'))});
document.querySelector('.search').addEventListener('input',e=>{const q=e.target.value.toLocaleLowerCase();let n=0;document.querySelectorAll('.chapters li').forEach(li=>{const ok=li.textContent.toLocaleLowerCase().includes(q);li.hidden=!ok;n+=ok});document.querySelector('.empty-search').style.display=n?'none':'block'});
document.querySelectorAll('.highlight').forEach(block=>{const pre=block.querySelector('pre');if(!pre)return;const b=document.createElement('button');b.type='button';b.className='copy';b.textContent='复制';b.setAttribute('aria-label','复制代码');b.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(pre.innerText)}catch(e){const t=document.createElement('textarea');t.value=pre.innerText;document.body.append(t);t.select();document.execCommand('copy');t.remove()}b.textContent='已复制';setTimeout(()=>b.textContent='复制',1200)});block.append(b)});
"""


def notebook_body(path: Path, destinations: dict[Path, str], output: Path):
    notebook = nbformat.read(path, as_version=4)
    exporter = HTMLExporter(template_name="basic")
    exporter.exclude_input_prompt = True
    exporter.exclude_output_prompt = True
    body, _ = exporter.from_notebook_node(notebook, resources={"metadata": {"path": str(path.parent)}})
    soup = BeautifulSoup(body, "html.parser")
    # Inline local images so generated pages retain all course illustrations.
    for image in soup.find_all("img", src=True):
        src = image["src"]
        if urlsplit(src).scheme or src.startswith("//"):
            continue
        image_path = (path.parent / unquote(urlsplit(src).path)).resolve()
        if not image_path.is_file():
            raise FileNotFoundError(f"{path.name}: missing image {src}")
        mime = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
        image["src"] = f"data:{mime};base64," + b64encode(image_path.read_bytes()).decode()
    for link in soup.find_all("a", href=True):
        href = link["href"]
        parts = urlsplit(href)
        if parts.scheme or href.startswith(("#", "//")):
            continue
        target = (path.parent / unquote(parts.path)).resolve()
        fragment = "#" + parts.fragment if parts.fragment else ""
        if target in destinations:
            link["href"] = destinations[target] + fragment
        elif target.is_relative_to(ROOT):
            # Repository-only references (slides, notices, validation) still work.
            link["href"] = GITHUB + "/blob/main/" + target.relative_to(ROOT).as_posix() + fragment
    toc = []
    for i, heading in enumerate(soup.find_all(["h1", "h2", "h3"])):
        if not heading.get("id"):
            heading["id"] = f"section-{i + 1}"
        toc.append((heading.name[-1], heading["id"], heading.get_text().strip().rstrip("¶")))
    return str(soup), toc


def build(output: Path):
    output.mkdir(parents=True, exist_ok=True)
    static = output / "_static"
    static.mkdir(exist_ok=True)
    (static / "style.css").write_text(CSS + HtmlFormatter().get_style_defs(".highlight"), encoding="utf-8")
    mathjax = static / "mathjax.js"
    if not mathjax.is_file():
        raise FileNotFoundError("缺少 course_content/html/_static/mathjax.js；请保留仓库中的预览资源。")
    paths = [ROOT / "index.ipynb"] + sorted((ROOT / "course_content/tutorials").glob("*.ipynb"))
    destinations = {p.resolve(): p.stem + ".html" for p in paths}
    for i, path in enumerate(paths):
        title = TITLES.get(path.stem, path.stem)
        body, headings = notebook_body(path, destinations, output)
        chapters = "".join(f'<li><a class="{"active" if p == path else ""}" href="{destinations[p.resolve()]}" {"aria-current=page" if p == path else ""}>{html.escape(TITLES.get(p.stem,p.stem))}</a></li>' for p in paths)
        toc = "".join(f'<a class="depth-{depth}" href="#{html.escape(anchor,quote=True)}">{html.escape(text)}</a>' for depth, anchor, text in headings)
        previous = f'<a rel="prev" href="{paths[i-1].stem}.html">← {html.escape(TITLES.get(paths[i-1].stem,paths[i-1].stem))}</a>' if i else '<span></span>'
        following = f'<a rel="next" href="{paths[i+1].stem}.html">{html.escape(TITLES.get(paths[i+1].stem,paths[i+1].stem))} →</a>' if i+1 < len(paths) else '<span></span>'
        source = GITHUB + "/blob/main/" + path.relative_to(ROOT).as_posix()
        page = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} — NVIDIA DLI at ModelScope Notebook</title><link rel="stylesheet" href="_static/style.css">
<script>window.MathJax={{tex:{{inlineMath:[['$','$'],['\\\\(','\\\\)']],displayMath:[['$$','$$'],['\\\\[','\\\\]']] }},options:{{enableMenu:false}},svg:{{fontCache:'global'}}}};</script><script defer src="_static/mathjax.js"></script></head>
<body><header class="topbar"><button class="menu" aria-label="打开课程目录" aria-expanded="false">☰</button><a class="brand" href="index.html">NVIDIA DLI · 深度学习基础</a><nav class="toplinks" aria-label="相关链接"><a href="{source}">源 Notebook</a><a href="{GALLERY}">魔搭运行</a><a href="{GITHUB}">GitHub</a></nav></header>
<aside class="sidebar" aria-label="课程目录"><input class="search" type="search" placeholder="搜索课程…" aria-label="搜索课程"><h2>课程目录</h2><ul class="chapters">{chapters}</ul><p class="empty-search">没有匹配的课程</p></aside>
<main><div class="breadcrumb"><a href="index.html">深度学习基础</a> / {html.escape(title)}</div><h1 class="page-title">{html.escape(title)}</h1><div class="subtitle">NVIDIA DLI at ModelScope Notebook · VoyagerX 适配</div><article class="notebook">{body}</article><nav class="pager" aria-label="上一课与下一课">{previous}{following}</nav><footer class="footer">原课程 © 2026 NVIDIA CORPORATION &amp; AFFILIATES · 代码 Apache-2.0 / 正文 CC-BY-4.0 · 适配与预览构建：VoyagerX<br>第三方归属见 <a href="{GITHUB}/blob/main/THIRD_PARTY_NOTICES.md">素材来源说明</a>。</footer></main><aside class="toc" aria-label="本页目录"><h2>本页目录</h2>{toc}</aside><script>{JS}</script></body></html>'''
        (output / destinations[path.resolve()]).write_text(page, encoding="utf-8")
        print(f"Built {path.name} → {destinations[path.resolve()]}")
    print(f"预览入口：{output / 'index.html'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "course_content/html")
    args = parser.parse_args()
    build(args.output.resolve())
