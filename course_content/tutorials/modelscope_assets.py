"""ModelScope-only assets for the NVIDIA DLI course; no upstream network fallback."""
import os
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
from pathlib import Path
import gzip
import shutil
import zipfile
from modelscope.hub.snapshot_download import dataset_snapshot_download, snapshot_download

ASSET_DIR = Path(os.environ.get('DLI_ASSET_DIR', './tutorial_assets')).resolve()
REPOS = {
    'mnist': 'VoyagerX/mnist',
    'asl': 'VoyagerX/asl-hg',
    'corgi': 'VoyagerX/penny-the-corgi',
    'vgg16': 'VoyagerX/vgg16-imagenet1k',
    'bert-base-cased': 'VoyagerX/bert-base-cased',
    'bert-large-uncased-whole-word-masking-finetuned-squad':
        'VoyagerX/bert-large-uncased-whole-word-masking-finetuned-squad',
}

def _fetch(kind, repo_id, patterns, required):
    target = ASSET_DIR / kind / repo_id.split('/', 1)[1]
    if not all((target / name).is_file() for name in required):
        downloader = dataset_snapshot_download if kind == 'datasets' else snapshot_download
        downloader(repo_id=repo_id, local_dir=str(target),
                   allow_patterns=patterns + ['README.md', 'LICENSE', 'manifest.json'],
                   max_workers=4, endpoint='https://modelscope.cn')
    missing = [name for name in required if not (target / name).is_file()]
    if missing:
        raise FileNotFoundError(f'{repo_id}: missing files {missing}')
    return target

def prepare_mnist(data_dir='data'):
    names = ['train-images-idx3-ubyte', 'train-labels-idx1-ubyte',
             't10k-images-idx3-ubyte', 't10k-labels-idx1-ubyte']
    raw = Path(data_dir) / 'MNIST' / 'raw'
    if all((raw / name).is_file() for name in names):
        return Path(data_dir)
    source = _fetch('datasets', REPOS['mnist'], ['raw/*.gz'],
                    ['raw/' + name + '.gz' for name in names])
    raw.mkdir(parents=True, exist_ok=True)
    for name in names:
        if not (raw / name).is_file():
            with gzip.open(source / 'raw' / (name + '.gz'), 'rb') as stream:
                with open(raw / name, 'wb') as output:
                    shutil.copyfileobj(stream, output)
    return Path(data_dir)

def prepare_asl(data_dir='data/asl_data'):
    import pandas as pd
    names = ['sign_mnist_train.csv', 'sign_mnist_valid.csv']
    expected = [(19200, 785), (4800, 785)]
    target = Path(data_dir)
    def read_complete(folder):
        frames = tuple(pd.read_csv(folder / name) for name in names)
        for frame, shape in zip(frames, expected):
            if frame.shape != shape or sorted(frame['label'].unique().tolist()) != list(range(24)):
                raise ValueError('ASL cache is incomplete or uses a different label mapping')
        return frames
    if all((target / name).is_file() for name in names):
        try:
            return read_complete(target)
        except (ValueError, pd.errors.ParserError):
            print('Replacing incomplete local ASL cache from the course mirror')
    source = _fetch('datasets', REPOS['asl'], ['csv/*.csv', 'label_mapping.json'],
                    ['csv/' + name for name in names])
    read_complete(source / 'csv')
    target.mkdir(parents=True, exist_ok=True)
    for name in names:
        temporary = target / (name + '.tmp')
        shutil.copy2(source / 'csv' / name, temporary)
        temporary.replace(target / name)
    return read_complete(target)

def prepare_corgi(data_dir='data'):
    target = Path(data_dir)
    folder = target / 'PennyClassification'
    def complete():
        return all((folder / name).is_dir() and
                   sum(p.suffix.lower() in ('.jpg', '.jpeg', '.png') for p in (folder / name).iterdir()) == count
                   for name, count in [('Penny', 116), ('Not_Penny', 86)])
    if not complete():
        source = _fetch('datasets', REPOS['corgi'], ['penny-the-corgi.zip'],
                        ['penny-the-corgi.zip'])
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(source / 'penny-the-corgi.zip') as archive:
            for item in archive.infolist():
                destination = (target / item.filename).resolve()
                if not destination.is_relative_to(target.resolve()):
                    raise ValueError('Unsafe archive path')
            archive.extractall(target)
    for name in ['Penny', 'Not_Penny']:
        if not any((folder / name).iterdir()):
            raise FileNotFoundError(f'Empty class folder: {folder / name}')
    return folder

def load_vgg16():
    import torch
    from torchvision.models import vgg16
    folder = _fetch('models', REPOS['vgg16'], ['vgg16-397923af.pth'],
                    ['vgg16-397923af.pth'])
    model = vgg16(weights=None)
    state = torch.load(folder / 'vgg16-397923af.pth', map_location='cpu', weights_only=True)
    model.load_state_dict(state, strict=True)
    return model

def prepare_bert(name):
    if name not in ('bert-base-cased', 'bert-large-uncased-whole-word-masking-finetuned-squad'):
        raise ValueError(name)
    return str(_fetch('models', REPOS[name],
                      ['model.safetensors', '*.json', 'vocab.txt'],
                      ['model.safetensors', 'config.json', 'tokenizer_config.json', 'vocab.txt']))

def maybe_compile(model):
    # Opt-in; ordinary eager execution keeps the same training objective.
    if os.environ.get('DLI_USE_TORCH_COMPILE') == '1':
        import torch
        if not hasattr(torch, 'compile'):
            raise RuntimeError('torch.compile is unavailable')
        return torch.compile(model)
    return model
