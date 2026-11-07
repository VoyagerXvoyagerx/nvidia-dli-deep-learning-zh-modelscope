#!/usr/bin/env python3
"""Check course-specific answer disclosure without executing notebooks or training."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
import argparse,json,sys,threading
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_html import SOLUTION_GROUPS
from scripts.check_mobile import Handler
from playwright.sync_api import sync_playwright


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path);parser.add_argument('--screenshots',type=Path);args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(args.output.resolve())))
    threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
    groups=copies=0
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            for width in [390,1280]:
                for embedded in [False,True]:
                    context=browser.new_context(viewport={'width':width,'height':850},has_touch=width==390,is_mobile=width==390,permissions=['clipboard-read','clipboard-write'],reduced_motion='reduce')
                    page=context.new_page()
                    for name,expected in SOLUTION_GROUPS.items():
                        file=name+'.html';url=base+'/__iframe_test__?file='+quote(file) if embedded else base+'/'+file
                        page.goto(url,wait_until='load');frame=page.locator('iframe').element_handle().content_frame() if embedded else page.main_frame
                        frame.wait_for_function("document.querySelector('.code-actions') !== null")
                        details=frame.locator('details.solution');assert details.count()==len(expected)
                        for detail in details.all():
                            assert detail.get_attribute('open') is None
                            content=detail.locator('.solution-content');assert not content.is_visible()
                            summary=detail.locator('summary');summary.click();assert content.is_visible()
                            assert '点击收起解答' in summary.inner_text()
                            for block in content.locator('.highlight').all():
                                copy=block.locator('.copy');copy.scroll_into_view_if_needed()
                                pre=block.locator('pre');expected_text=pre.inner_text();copy.click()
                                page.wait_for_function('(expected)=>navigator.clipboard.readText().then(text=>text===expected)',arg=expected_text,timeout=5000)
                                geometry=block.evaluate('''b=>{const pre=b.querySelector('pre'),c=b.querySelector('.copy'),r=c.getBoundingClientRect(),p=pre.getBoundingClientRect(),s=getComputedStyle(pre);return {button:r.top+r.height/2,first:p.top+parseFloat(s.paddingTop)+parseFloat(s.lineHeight)/2}}''')
                                assert abs(geometry['button']-geometry['first'])<2,geometry;copies+=1
                            assert frame.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
                            if args.screenshots and not embedded and groups==0:
                                args.screenshots.mkdir(parents=True,exist_ok=True);page.screenshot(path=str(args.screenshots/f'{name}-{width}-open.png'))
                            summary.click();assert not content.is_visible();summary.focus();summary.press('Enter');assert content.is_visible();summary.press('Enter');assert not content.is_visible();groups+=1
                        print('Passed',name,width,'iframe' if embedded else 'standalone',flush=True)
                    context.close()
            browser.close()
    finally:server.shutdown();server.server_close()
    print(json.dumps({'solution_toggle_cases':groups,'solution_copy_cases':copies,'notebook_execution':False}),flush=True)

if __name__=='__main__':main()
