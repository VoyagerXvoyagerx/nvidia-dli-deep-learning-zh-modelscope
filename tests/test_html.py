import tempfile
import re
import unittest
from pathlib import Path

import nbformat
from bs4 import BeautifulSoup
import build_html
from scripts.sync_index import entry_markdown


class HtmlTests(unittest.TestCase):
    def test_preview_links_hidden_cells_and_unchanged_notebooks(self):
        root = build_html.ROOT
        notebooks = [root / 'index.ipynb', *sorted((root / 'course_content/tutorials').glob('*.ipynb'))]
        originals = {p: p.read_bytes() for p in notebooks}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / '_static').mkdir()
            (output / '_static/mathjax.js').write_text('')
            build_html.build(output)
            for path in notebooks:
                with self.subTest(notebook=path.name):
                    page = (output / (path.stem + '.html')).read_text()
                    soup = BeautifulSoup(page, 'html.parser')
                    links = soup.select('.toplinks a')
                    self.assertEqual([a.text for a in links], ['查看和运行 Notebook', 'GitHub'])
                    for link in links:
                        self.assertEqual(link.get('target'), '_blank')
                        self.assertIn('noopener', link.get('rel', []))
                    self.assertEqual(links[0]['href'], build_html.GALLERY + '/files/' + path.relative_to(root).as_posix())
                    self.assertNotIn('本版本由 VoyagerX 适配', page)
                    self.assertNotIn('tutorial_dir', page)
                    if path.stem != 'index':
                        self.assertNotIn('%cd', page)
                    self.assertIn('NVIDIA_Training_and_Certification', links[0]['href'])
                    self.assertTrue(soup.select_one('article').get_text(strip=True))
                    self.assertIsNone(soup.select_one('.subtitle'))
                    self.assertNotIn('NVIDIA DLI at ModelScope Notebook · VoyagerX 适配', page)
                    self.assertEqual(path.read_bytes(), originals[path])
                    if path.stem == 'index':
                        courses = next(h for h in soup.select('article h2') if h.get_text(strip=True).rstrip('¶') == '开源课程')
                        course_links = courses.find_next_sibling('ul').select('li a')
                        self.assertEqual([a.get_text() for a in course_links], ['深度学习基础 >', 'NVIDIA 开源课程目录 >'])
                        readme = (root / 'README.md').read_text()
                        self.assertEqual(nbformat.read(path, as_version=4).cells[0].source, entry_markdown(readme))
                        tracking = re.findall(r'\]\((https?://[^)]+[?&]ncid=[^)]+)\)', readme)
                        self.assertTrue(tracking)
                        article_links = [a['href'] for a in soup.select('article a[href]')]
                        for url in tracking:
                            self.assertEqual(article_links.count(url), tracking.count(url))
                        for link in soup.select('a[href]'):
                            if not link['href'].startswith('#'):
                                self.assertEqual(link.get('target'), '_blank')
                                self.assertIn('noopener', link.get('rel', []))
                        slides = soup.select('article a[href$=".pptx"]')
                        self.assertEqual(len(slides), 6)
                        for slide in slides:
                            self.assertTrue(slide['href'].startswith(build_html.GITHUB + '/raw/refs/heads/main/course_content/slides/'))
                            self.assertEqual(slide.get('target'), '_blank')
                            self.assertIn('noopener', slide.get('rel', []))
