"""Run the Notebook's real training loop on a small CPU dataset with a singleton tail."""
import contextlib
import io
import json
from pathlib import Path
import unittest

try:
    import torch
except ImportError:
    torch = None


@unittest.skipIf(torch is None, 'Training regression requires PyTorch; HTML builds do not install it')
class CorgiTrainingTests(unittest.TestCase):
    def test_training_keeps_the_last_single_sample_batch(self):
        path = Path(__file__).resolve().parents[1] / 'course_content/tutorials/05b_corgi_door.ipynb'
        notebook = json.loads(path.read_text())
        torch.manual_seed(0)
        model = torch.nn.Linear(4, 1)
        before = model.weight.detach().clone()
        loader = torch.utils.data.DataLoader(torch.utils.data.TensorDataset(
            torch.randn(161, 4), torch.randint(0, 2, (161,)).float()), batch_size=32)
        shapes = []
        criterion = torch.nn.BCEWithLogitsLoss()

        def loss_function(output, labels):
            shapes.append((output.shape, labels.shape))
            return criterion(output, labels)

        namespace = dict(torch=torch, device=torch.device('cpu'), train_loader=loader,
                         train_N=161, random_trans=lambda x: x, loss_function=loss_function,
                         optimizer=torch.optim.Adam(model.parameters()))
        for prefix in ['def get_batch_accuracy(', 'def train(']:
            source = next(''.join(c['source']) for c in notebook['cells']
                          if c['cell_type'] == 'code' and ''.join(c['source']).startswith(prefix))
            exec(compile(source, str(path), 'exec'), namespace)
        with contextlib.redirect_stdout(io.StringIO()):
            namespace['train'](model)
        self.assertEqual([shape[0] for shape in shapes], [(32,)] * 5 + [(1,)])
        self.assertTrue(all(output == labels for output, labels in shapes))
        self.assertTrue(torch.isfinite(model.weight).all())
        self.assertFalse(torch.equal(model.weight.detach(), before))
