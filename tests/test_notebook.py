import ast
import sys
import unittest
from nbloader import ROOT, notebook, load_notebook


class NotebookTests(unittest.TestCase):
    def test_structure_and_outputs(self):
        nb = notebook()
        self.assertEqual((nb['nbformat'], nb['nbformat_minor']), (4, 5))
        ids = [cell['id'] for cell in nb['cells']]
        self.assertEqual(len(ids), len(set(ids)))
        original = ['175bf3fb', '5c8468fb', '403835be', '454ee782', '3091daf0', '7b3f507d', '506a753b']
        self.assertEqual([item for item in ids if item in original], original)
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                self.assertEqual(cell['outputs'], [])
                self.assertIsNone(cell['execution_count'])
                compile(''.join(cell['source']), cell['id'], 'exec')

    def test_core_is_standard_library_only(self):
        cells = [c for c in notebook()['cells'] if 'core' in c['metadata'].get('tags', [])]
        self.assertEqual(len(cells), 2)
        imports = []
        for cell in cells:
            tree = ast.parse(''.join(cell['source']))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name.split('.')[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module.split('.')[0])
        self.assertTrue(imports)
        self.assertTrue(set(imports) <= sys.stdlib_module_names)
        self.assertTrue(callable(load_notebook().build_query))

    def test_safe_requests_and_no_package_dependency(self):
        source = '\n'.join(''.join(c['source']) for c in notebook()['cells'])
        # ユーザー承認：matplotlib同梱スタイル名だけを例外にする。
        self.assertEqual(source.count('seaborn-v0_8-whitegrid'), 1)
        self.assertNotIn('seaborn', source.replace('seaborn-v0_8-whitegrid', ''))
        self.assertNotIn('time.time(', source)
        self.assertNotIn('!pip', source)
        self.assertNotIn('!git', source)
        calls = []
        for cell in notebook()['cells']:
            if cell['cell_type'] != 'code':
                continue
            for node in ast.walk(ast.parse(''.join(cell['source']))):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    owner = node.func.value
                    if node.func.attr == 'get' and isinstance(owner, ast.Name) and owner.id in ('requests', 'client'):
                        calls.append(node)
                        self.assertIn('timeout', [keyword.arg for keyword in node.keywords])
                        self.assertIn('allow_redirects', [keyword.arg for keyword in node.keywords])
        self.assertEqual(len(calls), 1)

    def test_workflow_without_install(self):
        workflow = (ROOT / '.github/workflows/test.yml').read_text(encoding='utf-8')
        for value in ('push', 'pull_request', 'contents: read', "'3.11'", "'3.12'",
                      'actions/checkout@v4', 'actions/setup-python@v5',
                      'python -m unittest discover -s tests -v'):
            self.assertIn(value, workflow)
        self.assertNotIn('pip install', workflow)
