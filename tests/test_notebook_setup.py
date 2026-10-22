import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SetupTests(unittest.TestCase):
    def test_single_cd_and_existing_helper_paths(self):
        paths = [ROOT / 'index.ipynb', ROOT / 'smoke_test.ipynb', *sorted((ROOT / 'course_content/tutorials').glob('*.ipynb'))]
        for p in paths:
            with self.subTest(notebook=p.name):
                nb = json.loads(p.read_text())
                init = ''.join(nb['cells'][1]['source'])
                self.assertEqual(init.count('%cd '), 1)
                self.assertIn('NVIDIA_Training_and_Certification_NVIDIA-DLI-Deep-Learning-ZH-ModelScope/course_content/tutorials', init)
                self.assertIn('hide-web', nb['cells'][1]['metadata']['tags'])
                for old in ['requests', 'sys.path', 'rglob', 'os.chdir', 'python -c', 'tutorial_dir']:
                    self.assertNotIn(old, init)
        self.assertTrue((ROOT / 'course_content/tutorials/modelscope_assets.py').is_file())
        self.assertTrue((ROOT / 'course_content/tutorials/utils.py').is_file())
        self.assertTrue((ROOT / 'course_content/tutorials/data').is_dir())
