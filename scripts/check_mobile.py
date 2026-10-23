#!/usr/bin/env python3
"""Browser regression checks for generated Notebook pages (no notebook execution).

Serve the output over HTTP and test both standalone pages and a sandboxed iframe.
The iframe is a layout harness, not a replacement for testing the actual Gallery.
Install: pip install playwright==1.55.0; python -m playwright install chromium
Run: python scripts/check_mobile.py course_content/html --screenshots /tmp/mobile-qa
"""
from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import parse_qs, quote, urlsplit

from playwright.sync_api import sync_playwright


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        if urlsplit(self.path).path != '/__iframe_test__':
            return super().do_GET()
        name = parse_qs(urlsplit(self.path).query)['file'][0]
        # Simulate the platform header and top-right fullscreen control.
        markup = f'''<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1">
<style>*{{box-sizing:border-box}}body{{margin:0}}header{{height:40px;background:#eee}}
iframe{{display:block;width:100%;height:calc(100dvh - 40px);border:0}}
button{{position:fixed;top:40px;right:0;width:48px;height:48px;z-index:100}}</style>
<header>Gallery iframe layout test</header><button aria-label="平台全屏">⛶</button>
<iframe title="课程" sandbox="allow-scripts allow-same-origin allow-popups" src="/{quote(name, safe='/')}"></iframe>'''
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(markup.encode())


def check_page(page, frame, width, mobile):
    frame.wait_for_function("document.querySelector('.nav-backdrop') !== null")
    frame.evaluate('() => document.fonts.ready')
    dimensions = frame.evaluate('''() => ({width:innerWidth,scroll:document.documentElement.scrollWidth,
      body:document.body.scrollWidth,overflow:getComputedStyle(document.body).overflowX})''')
    assert dimensions['scroll'] <= width + 1 and dimensions['body'] <= width + 1, dimensions
    assert dimensions['overflow'] not in ['hidden', 'clip'], 'Do not mask page overflow'
    if mobile:
        sidebar = frame.locator('.sidebar')
        assert sidebar.get_attribute('aria-hidden') == 'true'
        assert not sidebar.is_visible(), 'Drawer must really be hidden, not only aria-collapsed'
        assert sidebar.evaluate('(el) => el.inert')
        assert frame.locator('.menu').bounding_box()['height'] >= 44
        assert frame.locator('.brand').bounding_box()['x'] + frame.locator('.brand').bounding_box()['width'] <= width - 48
        frame.locator('.menu').click()
        sidebar.wait_for(state='visible')
        assert frame.locator('.nav-backdrop').is_visible()
        assert not sidebar.evaluate('(el) => el.inert')
        for link in frame.locator('.drawer-actions a').all():
            assert link.is_visible() and link.bounding_box()['height'] >= 44
            assert link.get_attribute('target') == '_blank'
        frame.locator('.menu-close').click()
        sidebar.wait_for(state='hidden')
        frame.locator('.menu').click()
        page.keyboard.press('Escape')
        sidebar.wait_for(state='hidden')
        frame.locator('.menu').click()
        # Click the visible part of the backdrop outside the drawer.
        box = frame.locator('.nav-backdrop').bounding_box()
        page.mouse.click(box['x'] + box['width'] - 12, box['y'] + 120)
        sidebar.wait_for(state='hidden')
    else:
        assert frame.locator('.sidebar').is_visible()
        assert not frame.locator('.menu').is_visible()
        for link in frame.locator('.toplinks a').all():
            box = link.bounding_box()
            assert link.is_visible() and box['x'] + box['width'] <= width - 48

    checked = 0
    for pre in frame.locator('.notebook pre').all():
        if not pre.evaluate('(el) => el.scrollWidth > el.clientWidth + 2'):
            continue
        controls = pre.locator('xpath=following-sibling::*[1]')
        slider = controls.locator('.code-scrollbar')
        assert controls.is_visible(), 'Overflowing code must expose its drag control'
        slider.press('End')
        assert pre.evaluate('(el) => el.scrollLeft > 0'), 'Slider must scroll the actual code'
        slider.press('Home')
        assert pre.evaluate('(el) => el.scrollLeft < 2')
        # Exercise an actual pointer drag, not a synthetic value assignment.
        box = slider.bounding_box()
        page.mouse.move(box['x'] + 8, box['y'] + box['height']/2)
        page.mouse.down()
        page.mouse.move(box['x'] + box['width'] - 8, box['y'] + box['height']/2, steps=8)
        page.mouse.up()
        assert pre.evaluate('(el) => el.scrollLeft > 0'), 'Scrollbar drag failed'
        slider.press('Home')
        checked += 1
        if checked == 2:
            break
    assert frame.evaluate('window.scrollX') == 0, 'Code scrolling must not scroll the page sideways'
    return checked


def check_touch(page, frame):
    for pre in frame.locator('.notebook pre').all():
        if not pre.evaluate('(el) => el.scrollWidth > el.clientWidth + 40'):
            continue
        pre.scroll_into_view_if_needed()
        slider = pre.locator('xpath=following-sibling::*[1]').locator('input')
        slider.press('Home')
        pre.scroll_into_view_if_needed()
        box = pre.bounding_box()
        cdp = page.context.new_cdp_session(page)
        start = box['x'] + box['width'] - 24
        y = min(box['y'] + box['height'] - 18, page.viewport_size['height'] - 30)
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': start, 'y': y}]})
        for i in range(1, 9):
            cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': start - i * (box['width'] - 48)/8, 'y': y}]})
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        cdp.detach()
        pre.evaluate('(el) => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')
        assert pre.evaluate('(el) => el.scrollLeft > 0'), 'Touch swipe must move code horizontally'
        assert frame.evaluate('window.scrollX') == 0
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--screenshots', type=Path)
    args = parser.parse_args()
    root = args.output.resolve()
    files = sorted(root.rglob('*.html'))
    assert files, f'No generated pages in {root}'
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}'
    results, touches, scroll_checks = [], 0, 0
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for width in [320, 375, 390, 768, 820, 1024, 1280]:
                print(f'Checking {width}px: standalone and iframe', flush=True)
                context = browser.new_context(viewport={'width': width, 'height': 850},
                                              is_mobile=width <= 1024, has_touch=width <= 1024,
                                              device_scale_factor=1, reduced_motion='reduce')
                page = context.new_page()
                for embedded in [False, True]:
                    for path in files:
                        name = path.relative_to(root).as_posix()
                        url = f'{base}/__iframe_test__?file={quote(name, safe="")}' if embedded else f'{base}/{quote(name)}'
                        page.goto(url, wait_until='load')
                        frame = page.main_frame
                        if embedded:
                            frame = page.locator('iframe').element_handle().content_frame()
                            frame.wait_for_load_state('load')
                        scroll_checks += check_page(page, frame, width, width <= 1024)
                        if width == 390 and touches < (2 if embedded else 1):
                            touches += check_touch(page, frame)
                        results.append({'page': name, 'width': width, 'iframe': embedded})
                        if args.screenshots and width == 390 and embedded:
                            screenshot_base = args.screenshots / path.relative_to(root).with_suffix('')
                            screenshot_base.parent.mkdir(parents=True, exist_ok=True)
                            page.screenshot(path=str(screenshot_base.parent / f'{screenshot_base.name}-mobile.png'))
                            frame.locator('.menu').click()
                            page.screenshot(path=str(screenshot_base.parent / f'{screenshot_base.name}-drawer.png'))
                context.close()
                print(f'Passed {width}px', flush=True)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    # A text-only course may have no overflowing code; state that explicitly.
    print(json.dumps({'page_viewport_embedding_checks': len(results),
                      'code_scroll_checks': scroll_checks, 'touch_swipes': touches}, ensure_ascii=False))


if __name__ == '__main__':
    main()
