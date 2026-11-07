#!/usr/bin/env python3
"""Build a static, D2L-inspired course reader without executing notebooks.

Usage: python build_html.py
Dependencies: nbconvert, nbformat, beautifulsoup4 (included in the Notebook image).
"""
from __future__ import annotations

import argparse
import html
import hashlib
import json
import mimetypes
import re
from base64 import b64encode
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

import nbformat
from bs4 import BeautifulSoup
from nbconvert import HTMLExporter
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent
GITHUB = "https://github.com/VoyagerXvoyagerx/nvidia-dli-deep-learning-zh-modelscope"
GALLERY = "https://modelscope.cn/gallery/NVIDIA_Training_and_Certification/nvidia-dli-deep-learning-zh-modelscope"
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


# Manually reviewed solution cells for this course; unrelated discussion stays visible.
# IDs are stable Notebook cell IDs, not inferred matches for FIXME or source_hidden.
SOLUTION_GROUPS = {
    "02_asl": [("792987bf",), ("0fd9a9d9",), ("dda16941",)],
    "03_asl_cnn": [("be08df74",), ("8fa693ac",), ("5ef43048", "baa0ddff")],
    "04b_asl_predictions": [("1108bf8b",)],
    "05a_doggy_door": [("b52d3bed",)],
    "05b_corgi_door": [("30f11578",)],
}


def fold_solutions(soup: BeautifulSoup, notebook_stem: str) -> None:
    """Wrap only individually reviewed answer cells; never edit Notebook sources."""
    for ids in SOLUTION_GROUPS.get(notebook_stem, []):
        cells = [soup.find(id="cell-id=" + cell_id) for cell_id in ids]
        if any(cell is None for cell in cells):
            raise ValueError(f"{notebook_stem}: solution cells changed; review mapping {ids}")
        if any("# SOLUTION" not in cell.get_text() for cell in cells):
            raise ValueError(f"{notebook_stem}: mapped cell is no longer a solution: {ids}")
        if any(a.find_next_sibling() is not b for a,b in zip(cells,cells[1:])):
            raise ValueError(f"{notebook_stem}: solution cells are no longer adjacent: {ids}")
        details = soup.new_tag("details", attrs={"class": "solution", "data-solution-cells": ",".join(ids)})
        summary = soup.new_tag("summary")
        dots = soup.new_tag("span", attrs={"class": "solution-dots", "aria-hidden": "true"});dots.string = "…"
        show = soup.new_tag("span", attrs={"class": "solution-show"});show.string = "点击展开解答"
        hide = soup.new_tag("span", attrs={"class": "solution-hide"});hide.string = "点击收起解答"
        summary.extend([dots,show,hide]);details.append(summary)
        content = soup.new_tag("div", attrs={"class": "solution-content"});details.append(content)
        cells[0].insert_before(details)
        for cell in cells:content.append(cell.extract())


CSS = r"""
:root{--blue:#1976d2;--ink:#37474f;--muted:#697b86;--line:#e5ebef;--header-height:64px}
*{box-sizing:border-box}html{width:100%;scroll-behavior:smooth;scroll-padding-top:82px}body{width:100%;min-width:0;margin:0;color:var(--ink);background:#fff;font:16px/1.85 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans SC","Microsoft YaHei",sans-serif}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}button,input{font:inherit}button:focus-visible,a:focus-visible,input:focus-visible,pre:focus-visible{outline:3px solid #ffb300;outline-offset:2px}
.topbar{height:var(--header-height);position:fixed;inset:0 0 auto;background:var(--blue);color:#fff;display:flex;align-items:center;gap:24px;padding:0 24px;z-index:20;box-shadow:0 2px 6px #0002;min-width:0}
.brand{font-size:19px;font-weight:600;color:#fff;min-width:0}.toplinks{margin-left:auto;margin-right:56px;display:flex;align-items:center;gap:20px;flex-shrink:0}.toplinks a{color:#fff;font-size:14px;min-height:44px;display:flex;align-items:center}.menu{display:none;border:0;background:none;color:#fff;font-size:24px;cursor:pointer}
.sidebar{position:fixed;top:var(--header-height);bottom:0;left:0;width:280px;padding:28px 20px 40px;overflow-y:auto;overscroll-behavior-y:contain;border-right:1px solid var(--line);background:#fafcfd;z-index:15}
.sidebar h2,.toc h2{font-size:14px;margin:0 0 16px;color:var(--muted);font-weight:500}.search{width:100%;min-height:44px;padding:10px 12px;border:1px solid #d7e0e5;border-radius:4px;background:#fff;font-size:16px;margin-bottom:20px}
.chapters{list-style:none;padding:0;margin:0}.chapters li{margin:3px 0}.chapters a{display:flex;align-items:center;min-height:44px;padding:8px 12px;border-radius:3px;font-size:14px;color:#455a64;line-height:1.65;overflow-wrap:anywhere}.chapters a.active{background:#e3f2fd;color:var(--blue);font-weight:600;border-left:3px solid var(--blue)}
main{margin:var(--header-height) 230px 0 280px;padding:36px 40px 52px;max-width:1140px;min-width:0;min-height:calc(100vh - var(--header-height))}.breadcrumb{font-size:13px;color:var(--muted);margin-bottom:17px;overflow-wrap:anywhere}.page-title{font-size:32px;line-height:1.4;font-weight:500;margin:0 0 12px;overflow-wrap:anywhere}
.toc{position:fixed;right:0;top:94px;width:230px;padding:10px 24px;max-height:calc(100vh - 110px);overflow:auto;border-left:1px solid var(--line)}.toc a{display:block;font-size:12px;line-height:1.7;margin:9px 0;color:var(--muted)}.toc a.depth-3{padding-left:12px}
.notebook{width:100%;min-width:0;max-width:100%;overflow-wrap:anywhere}.notebook h1{font-size:28px}.notebook h2{font-size:24px}.notebook h3{font-size:20px}.notebook h4{font-size:17px}.notebook h1,.notebook h2,.notebook h3,.notebook h4{font-weight:500;line-height:1.5;margin:32px 0 15px;overflow-wrap:anywhere}
.notebook p{margin:12px 0}.notebook p,.notebook li,.notebook a{white-space:normal;overflow-wrap:anywhere;word-break:normal}.notebook img{display:inline-block;max-width:100%!important;height:auto!important}.notebook video,.notebook iframe{max-width:100%}
.cell,.inner_cell,.text_cell,.text_cell_render,.rendered_html,.input,.input_area,.output_wrapper,.output,.output_area,.output_subarea{min-width:0;max-width:100%;width:auto}.text_cell_render{padding:0}.input_area{width:100%}.cell{margin:20px 0}.prompt,.anchor-link{display:none}
.notebook blockquote{border-left:4px solid #90caf9;background:#f4f9fd;padding:8px 16px;margin:20px 0}.notebook ul,.notebook ol{padding-left:24px}.notebook table{border-collapse:collapse;font-size:14px;margin:0}.notebook th,.notebook td{border:1px solid #dfe6ea;padding:10px 13px;vertical-align:top}.notebook th{background:#f5f8fa}.table-scroll{width:100%;max-width:100%;min-width:0;overflow-x:auto;overscroll-behavior-x:contain;-webkit-overflow-scrolling:touch;margin:20px 0}.table-scroll table{width:max-content;min-width:100%;max-width:none}
code,pre{font:13px/1.65 ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace}p code,li code,td code{background:#f0f4f6;border-radius:3px;padding:2px 5px;color:#b33b56;white-space:normal;overflow-wrap:anywhere}
.highlight{--action-size:32px;--actions-width:72px;position:relative;width:100%;max-width:100%;min-width:0;padding-right:var(--actions-width);background:#f6f8fa!important;border:1px solid #e1e8ec;border-radius:6px;margin:16px 0;overflow:hidden}.highlight pre,.notebook pre.code-scroll{display:block;width:100%;max-width:100%;min-width:0;margin:0;padding:14px 14px 16px;overflow-x:auto;overflow-y:hidden;white-space:pre;word-break:normal;overflow-wrap:normal;tab-size:4;-webkit-overflow-scrolling:touch;overscroll-behavior-x:contain;touch-action:pan-x pan-y;scrollbar-width:auto;scrollbar-color:#8298a6 #e8eef2;background:transparent}
.output_area pre.code-scroll{padding:14px;background:#fbfcfd;border-left:3px solid #cfd8dc}.code-scroll code,.code-scroll span{white-space:pre;word-break:normal;overflow-wrap:normal}.code-scroll::-webkit-scrollbar,.table-scroll::-webkit-scrollbar{height:10px}.code-scroll::-webkit-scrollbar-track,.table-scroll::-webkit-scrollbar-track{background:#e8eef2}.code-scroll::-webkit-scrollbar-thumb,.table-scroll::-webkit-scrollbar-thumb{background:#8298a6;border-radius:6px}
.code-actions{position:absolute;right:4px;top:calc(var(--code-line-center,22.125px) - var(--action-size)/2);display:flex;align-items:center;gap:4px;z-index:1}.code-actions .copy,.code-actions .run-code{display:inline-flex;align-items:center;justify-content:center;flex:0 0 var(--action-size);width:var(--action-size);height:var(--action-size);border:0;border-radius:4px;padding:0;background:transparent;color:#607d8b;cursor:pointer;text-decoration:none}.code-actions svg{width:18px;height:18px;pointer-events:none}.code-actions .copy:hover,.code-actions .run-code:hover,.code-actions .copy:focus-visible,.code-actions .run-code:focus-visible{background:#e3f2fd;color:var(--blue)}.code-actions .copy:focus-visible,.code-actions .run-code:focus-visible{outline-offset:-3px}.code-actions .copy.copied{color:#2e7d32}.code-tooltip{position:fixed;z-index:100;max-width:calc(100vw - 16px);padding:7px 10px;border-radius:4px;background:#263238;color:#fff;font-size:13px;line-height:1.5;box-shadow:0 2px 8px #0003;pointer-events:none;white-space:nowrap}.code-tooltip[hidden]{display:none}
.MathJax{max-width:100%;overflow-x:auto;overflow-y:hidden}.MathJax[display="true"]{display:block}.MathJax svg{max-width:none}.pager{display:flex;justify-content:space-between;gap:20px;margin-top:44px;padding-top:22px;border-top:1px solid var(--line);font-size:14px}.pager a{min-height:44px;display:flex;align-items:center;overflow-wrap:anywhere;min-width:0}.footer{margin-top:30px;color:var(--muted);font-size:12px;overflow-wrap:anywhere}.empty-search{font-size:13px;color:var(--muted);display:none}
.solution{border:1px solid var(--line);border-radius:6px;margin:18px 0;background:#fafcfd;min-width:0;max-width:100%}.solution summary{display:flex;align-items:center;gap:10px;min-height:44px;padding:8px 14px;cursor:pointer;color:var(--blue);font-size:14px;list-style:none;user-select:none}.solution summary::-webkit-details-marker{display:none}.solution summary:focus-visible{outline:3px solid #ffb300;outline-offset:2px}.solution-dots{font-size:22px;line-height:1}.solution[open] .solution-show,.solution:not([open]) .solution-hide{display:none}.solution-content{padding:0 12px 4px;min-width:0}.solution-content>.cell{margin:10px 0}.solution-content .highlight{margin:10px 0}
.drawer-head,.drawer-actions,.nav-backdrop{display:none}.nav-backdrop[hidden]{display:none!important}
@media(min-width:1800px){main{margin-left:calc(280px + (100vw - 1800px)/2)}}
@media(max-width:1200px){.toc{display:none}main{margin-right:0;padding:30px}}
@media(max-width:1024px){
 :root{--header-height:60px}html{scroll-padding-top:76px}.topbar{gap:10px;padding:0 64px 0 12px}.menu{display:flex;align-items:center;justify-content:center;flex:0 0 44px;width:44px;height:44px;padding:0}.brand{font-size:16px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.4}.toplinks{display:none}.toc{display:none}
 .sidebar{top:0;bottom:0;width:min(320px,calc(100vw - 48px));max-width:100%;padding:16px 16px 32px;z-index:50;transform:translateX(-105%);visibility:hidden;pointer-events:none;transition:transform .18s ease,visibility .18s;background:#fff;box-shadow:8px 0 30px #0003;height:100dvh;max-height:100dvh}
 .sidebar.open{display:block;transform:translateX(0);visibility:visible;pointer-events:auto}.drawer-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:16px;font-size:18px}.menu-close{border:0;background:#eff4f8;color:#37474f;border-radius:4px;font-size:26px;width:44px;height:44px;cursor:pointer}.drawer-actions{display:flex;flex-direction:column;gap:4px;border-top:1px solid var(--line);margin-top:20px;padding-top:14px}.drawer-actions a{display:flex;align-items:center;min-height:44px;padding:8px 12px;font-size:14px}
 .nav-backdrop{display:block;position:fixed;inset:0;border:0;background:#0006;z-index:40;padding:0;cursor:pointer}.nav-open{overflow:hidden}.chapters a{min-height:44px}main{width:auto;min-width:0;margin:var(--header-height) 0 0;padding:24px 20px 40px;max-width:100%;min-height:calc(100dvh - var(--header-height))}.page-title{font-size:26px}.notebook h1{font-size:25px}.notebook h2{font-size:22px}.notebook h3{font-size:19px}.highlight{--action-size:44px;--actions-width:96px}.pager{flex-wrap:wrap}.table-scroll{max-width:100%}
}
@media(max-width:480px){main{padding:22px 16px 36px}.topbar{padding-right:60px}.brand{font-size:15px}.page-title{font-size:24px}.notebook h1{font-size:23px}.notebook h2{font-size:21px}.notebook blockquote{margin-left:0;margin-right:0;padding:8px 12px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.sidebar{transition:none}}
"""

JS = r"""
(()=>{
 const sidebar=document.querySelector('.sidebar'),menu=document.querySelector('.menu');
 const mobile=matchMedia('(max-width:1024px)');
 sidebar.id='course-navigation';menu.setAttribute('aria-controls',sidebar.id);
 const heading=document.createElement('div');heading.className='drawer-head';
 const headingText=document.createElement('strong');headingText.textContent='课程目录';
 const close=document.createElement('button');close.type='button';close.className='menu-close';close.setAttribute('aria-label','关闭课程目录');close.textContent='×';heading.append(headingText,close);sidebar.prepend(heading);
 const actions=document.createElement('nav');actions.className='drawer-actions';actions.setAttribute('aria-label','Notebook 与源码');
 document.querySelectorAll('.toplinks a').forEach(link=>actions.append(link.cloneNode(true)));sidebar.append(actions);
 const backdrop=document.createElement('button');backdrop.type='button';backdrop.className='nav-backdrop';backdrop.hidden=true;backdrop.tabIndex=-1;backdrop.setAttribute('aria-label','关闭课程目录遮罩');document.body.append(backdrop);
 let previousFocus;
 function setOpen(open,restore=true){
  open=!!open&&mobile.matches;
  if(open)previousFocus=document.activeElement;
  sidebar.classList.toggle('open',open);document.body.classList.toggle('nav-open',open);menu.setAttribute('aria-expanded',String(open));menu.setAttribute('aria-label',open?'关闭课程目录':'打开课程目录');backdrop.hidden=!open;
  sidebar.inert=mobile.matches&&!open;sidebar.setAttribute('aria-hidden',String(mobile.matches&&!open));
  if(open){sidebar.setAttribute('role','dialog');sidebar.setAttribute('aria-modal','true');close.focus()}
  else{sidebar.removeAttribute('role');sidebar.removeAttribute('aria-modal');if(restore&&previousFocus?.isConnected)previousFocus.focus()}
 }
 menu.addEventListener('click',()=>setOpen(!sidebar.classList.contains('open')));close.addEventListener('click',()=>setOpen(false));backdrop.addEventListener('click',()=>setOpen(false));
 sidebar.addEventListener('click',e=>{if(e.target.closest('a'))setOpen(false,false)});
 document.addEventListener('keydown',e=>{
  if(!sidebar.classList.contains('open'))return;
  if(e.key==='Escape'){e.preventDefault();setOpen(false)}
  if(e.key==='Tab'){
   const targets=[...sidebar.querySelectorAll('a[href],button,input')].filter(el=>el.getClientRects().length&&!el.disabled);const first=targets[0],last=targets.at(-1);
   if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}
  }
 });
 mobile.addEventListener('change',()=>setOpen(false,false));setOpen(false,false);
 document.querySelector('.search').addEventListener('input',e=>{
  const q=e.target.value.toLocaleLowerCase();let n=0;
  document.querySelectorAll('.chapters li').forEach(li=>{const ok=li.textContent.toLocaleLowerCase().includes(q);li.hidden=!ok;n+=ok});document.querySelector('.empty-search').style.display=n?'none':'block';
 });
 document.querySelectorAll('.notebook table').forEach(table=>{
  if(table.parentElement.classList.contains('table-scroll'))return;
  const wrapper=document.createElement('div');wrapper.className='table-scroll';wrapper.tabIndex=0;wrapper.setAttribute('role','region');wrapper.setAttribute('aria-label','表格，可左右滚动');table.before(wrapper);wrapper.append(table);
 });
 const icon=(paths)=>`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${paths}</svg>`;
 const playIcon=icon('<path d="m8 5 11 7-11 7Z"/>');
 const copyIcon=icon('<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h4"/>');
 const copiedIcon=icon('<path d="m5 12 4 4L19 6"/>');
 const tooltip=document.createElement('div');tooltip.className='code-tooltip';tooltip.id='code-action-tooltip';tooltip.setAttribute('role','tooltip');tooltip.hidden=true;document.body.append(tooltip);
 let tooltipOwner;
 function hideTooltip(){tooltip.hidden=true;tooltipOwner?.removeAttribute('aria-describedby');tooltipOwner=null}
 function showTooltip(owner,text=owner.dataset.tooltip){
  if(tooltipOwner!==owner)hideTooltip();tooltipOwner=owner;tooltip.textContent=text;tooltip.hidden=false;owner.setAttribute('aria-describedby',tooltip.id);
  const r=owner.getBoundingClientRect(),w=tooltip.offsetWidth,h=tooltip.offsetHeight;
  tooltip.style.left=Math.max(8,Math.min(innerWidth-w-8,r.left+(r.width-w)/2))+'px';
  tooltip.style.top=(r.top-h-8>=8?r.top-h-8:r.bottom+8)+'px';
 }
 function addTooltip(owner,label){
  owner.dataset.tooltip=label;owner.setAttribute('aria-label',label);
  owner.addEventListener('mouseenter',()=>showTooltip(owner));owner.addEventListener('focus',()=>showTooltip(owner));
  owner.addEventListener('mouseleave',hideTooltip);owner.addEventListener('blur',hideTooltip);
 }
 document.addEventListener('scroll',hideTooltip,true);window.addEventListener('resize',hideTooltip);window.addEventListener('blur',hideTooltip);document.addEventListener('keydown',e=>{if(e.key==='Escape')hideTooltip()});
 document.querySelectorAll('.notebook pre').forEach(pre=>{
  pre.classList.add('code-scroll');pre.tabIndex=0;pre.setAttribute('role','region');pre.setAttribute('aria-label','代码或输出内容，可左右滚动');
  const block=pre.closest('.highlight');
  if(block){
   const preStyle=getComputedStyle(pre);block.style.setProperty('--code-line-center',(parseFloat(preStyle.paddingTop)+parseFloat(preStyle.lineHeight)/2)+'px');
   const copy=document.createElement('button');copy.type='button';copy.className='copy';copy.innerHTML=copyIcon;addTooltip(copy,'复制');copy.addEventListener('click',async()=>{
    try{await navigator.clipboard.writeText(pre.innerText)}catch(e){const t=document.createElement('textarea');t.value=pre.innerText;document.body.append(t);t.select();document.execCommand('copy');t.remove()}
    copy.innerHTML=copiedIcon;copy.classList.add('copied');showTooltip(copy,'已复制');setTimeout(()=>{copy.innerHTML=copyIcon;copy.classList.remove('copied');if(tooltipOwner===copy){if(copy.matches(':hover')||document.activeElement===copy)showTooltip(copy);else hideTooltip()}},1200);
   });
   const run=document.createElement('a');run.className='run-code';run.innerHTML=playIcon;run.href='https://modelscope.cn/code/workspace?type=running&gid=cb1503c2-1458-4f67-b9c3-bd505091cb47';run.target='_blank';run.rel='noopener noreferrer';addTooltip(run,'在魔搭Notebook中运行');
   const toolbar=document.createElement('div');toolbar.className='code-actions';toolbar.append(run,copy);block.append(toolbar);
  }
 });
})();
"""


def notebook_body(path: Path, destinations: dict[Path, str], output: Path):
    notebook = nbformat.read(path, as_version=4)
    # 仅从 HTML 预览中隐藏适配说明与目录初始化，源 Notebook 保持完整。
    notebook.cells = [cell for cell in notebook.cells if not (
        "hide-web" in cell.metadata.get("tags", [])
        or
        (cell.cell_type == "markdown" and "原课程：NVIDIA DLI《深度学习基础》" in cell.source and "本版本由 VoyagerX 适配" in cell.source)
        or (cell.cell_type == "code" and 'tutorial_dir = Path("/mnt/workspace/fundamentals-of-deep-learning-zh/tutorials")' in cell.source)
        # IDE saves can drop tags; identify this course's initialization cell precisely.
        or (cell.cell_type == "code" and re.match(r"""^\s*%cd\s+["']/mnt/workspace/Gallery:.*?/course_content/tutorials["'](?:\n|$)""", cell.source))
    )]
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
            # Slides use GitHub's raw download route; notices use its file viewer.
            prefix = GITHUB + ("/raw/refs/heads/main/" if target.suffix.lower() in {".ppt", ".pptx"} else "/blob/main/")
            link["href"] = prefix + quote(target.relative_to(ROOT).as_posix(), safe="/") + fragment
    fold_solutions(soup, path.stem)
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
    stylesheet = CSS + HtmlFormatter().get_style_defs(".highlight")
    style_version = hashlib.sha256(stylesheet.encode()).hexdigest()[:12]
    (static / "style.css").write_text(stylesheet, encoding="utf-8")
    mathjax = static / "mathjax.js"
    if not mathjax.is_file():
        raise FileNotFoundError("缺少 course_content/html/_static/mathjax.js；请保留仓库中的预览资源。")
    paths = [ROOT / "index.ipynb"] + sorted((ROOT / "course_content/tutorials").glob("*.ipynb"))
    destinations = {p.resolve(): p.stem + ".html" for p in paths}
    for i, path in enumerate(paths):
        title = TITLES.get(path.stem, path.stem)
        body, headings = notebook_body(path, destinations, output)
        if path.stem == "index" and not body.strip():
            body = '<p>选择课程开始学习，点击“查看和运行 Notebook”进入对应文件完成练习。</p><ul>' + ''.join(
                f'<li><a href="{destinations[p.resolve()]}">{html.escape(TITLES.get(p.stem, p.stem))}</a></li>'
                for p in paths if p != path
            ) + '</ul>'
            body += '<h2>课程讲义（PPT）</h2><ul>' + ''.join(
                f'<li><a href="{GITHUB}/raw/refs/heads/main/{quote(slide.relative_to(ROOT).as_posix(), safe="/")}" target="_blank" rel="noopener noreferrer">{html.escape(slide.name)}</a></li>'
                for slide in sorted((ROOT / 'course_content/slides').glob('*.pptx'))
            ) + '</ul>'
        chapters = "".join(f'<li><a class="{"active" if p == path else ""}" href="{destinations[p.resolve()]}" {"aria-current=page" if p == path else ""}>{html.escape(TITLES.get(p.stem,p.stem))}</a></li>' for p in paths)
        toc = "".join(f'<a class="depth-{depth}" href="#{html.escape(anchor,quote=True)}">{html.escape(text)}</a>' for depth, anchor, text in headings)
        previous = f'<a rel="prev" href="{paths[i-1].stem}.html">← {html.escape(TITLES.get(paths[i-1].stem,paths[i-1].stem))}</a>' if i else '<span></span>'
        following = f'<a rel="next" href="{paths[i+1].stem}.html">{html.escape(TITLES.get(paths[i+1].stem,paths[i+1].stem))} →</a>' if i+1 < len(paths) else '<span></span>'
        source = GALLERY + "/files/" + path.relative_to(ROOT).as_posix()
        page = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} — NVIDIA DLI at ModelScope Notebook</title><link rel="stylesheet" href="_static/style.css?v={style_version}">
<script>window.MathJax={{tex:{{inlineMath:[['$','$'],['\\\\(','\\\\)']],displayMath:[['$$','$$'],['\\\\[','\\\\]']] }},options:{{enableMenu:false}},svg:{{fontCache:'global'}}}};</script><script defer src="_static/mathjax.js"></script></head>
<body><header class="topbar"><button class="menu" aria-label="打开课程目录" aria-expanded="false">☰</button><a class="brand" href="index.html">NVIDIA DLI · 深度学习基础</a><nav class="toplinks" aria-label="相关链接"><a href="{source}" target="_blank" rel="noopener noreferrer">查看和运行 Notebook</a><a href="{GITHUB}" target="_blank" rel="noopener noreferrer">GitHub</a></nav></header>
<aside class="sidebar" aria-label="课程目录"><input class="search" type="search" placeholder="搜索课程…" aria-label="搜索课程"><h2>课程目录</h2><ul class="chapters">{chapters}</ul><p class="empty-search">没有匹配的课程</p></aside>
<main><div class="breadcrumb"><a href="index.html">深度学习基础</a> / {html.escape(title)}</div><h1 class="page-title">{html.escape(title)}</h1><article class="notebook">{body}</article><nav class="pager" aria-label="上一课与下一课">{previous}{following}</nav><footer class="footer">原课程 © 2026 NVIDIA CORPORATION &amp; AFFILIATES · 代码 Apache-2.0 / 正文 CC-BY-4.0 · 适配与预览构建：VoyagerX<br>第三方归属见 <a href="{GITHUB}/blob/main/THIRD_PARTY_NOTICES.md">素材来源说明</a>。</footer></main><aside class="toc" aria-label="本页目录"><h2>本页目录</h2>{toc}</aside><script>{JS}</script></body></html>'''
        page_soup = BeautifulSoup(page, "html.parser")
        for link in page_soup.find_all("a", href=True):
            # 课程侧栏在当前预览页切换；外部链接保留新标签页。
            if link.find_parent("ul", class_="chapters"):
                link["target"] = "_self"
                continue
            if not link["href"].startswith("#"):
                link["target"] = "_blank"
                link["rel"] = list(dict.fromkeys([*link.get("rel", []), "noopener", "noreferrer"]))
        (output / destinations[path.resolve()]).write_text(str(page_soup), encoding="utf-8")
        print(f"Built {path.name} → {destinations[path.resolve()]}")
    print(f"预览入口：{output / 'index.html'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "course_content/html")
    args = parser.parse_args()
    build(args.output.resolve())
