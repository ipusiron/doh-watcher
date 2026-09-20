"""Load notebook cells using only the standard library."""
import json
from pathlib import Path
import types

ROOT = Path(__file__).resolve().parents[1]


def notebook():
    return json.loads((ROOT / 'doh_watcher.ipynb').read_text(encoding='utf-8'))


def load_notebook(tag='core'):
    cells = [cell for cell in notebook()['cells']
             if cell['cell_type'] == 'code' and tag in cell.get('metadata', {}).get('tags', [])]
    if not cells:
        raise ValueError('No code cells with requested tag')
    module = types.ModuleType('doh_core')
    source = '\n\n'.join(''.join(cell['source']) for cell in cells)
    exec(compile(source, str(ROOT / 'doh_watcher.ipynb') + ':' + tag, 'exec'), module.__dict__)
    return module
