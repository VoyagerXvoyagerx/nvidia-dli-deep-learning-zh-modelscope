import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup
import build_html


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
                    self.assertNotIn('%cd', page)
                    self.assertIn('NVIDIA_Training_and_Certification', links[0]['href'])
                    self.assertTrue(soup.select_one('article').get_text(strip=True))
                    self.assertEqual(path.read_bytes(), originals[path])
                    if path.stem == 'index':
                        slides = soup.select('article a[href$=".pptx"]')
                        self.assertEqual(len(slides), 6)
                        for slide in slides:
                            self.assertTrue(slide['href'].startswith(build_html.GITHUB + '/raw/refs/heads/main/course_content/slides/'))
                            self.assertEqual(slide.get('target'), '_blank')
                            self.assertIn('noopener', slide.get('rel', []))
