import ast
import re
import struct
import sys
import unittest
from nbloader import ROOT, notebook

README = (ROOT / 'README.md').read_text(encoding='utf-8')


class ReadmeTests(unittest.TestCase):
    def test_metadata_structure(self):
        match = re.match(r'<!--\s*---\n(.*?)\n---\s*-->', README, re.S)
        self.assertIsNotNone(match)
        metadata = match.group(1)
        keys = re.findall(r'^(\w+):', metadata, re.M)
        self.assertEqual(keys, ['id', 'slug', 'title', 'subtitle_ja', 'subtitle_en',
                                'description_ja', 'description_en', 'category_ja', 'category_en',
                                'difficulty', 'tags', 'repo_url', 'demo_url', 'hub'])
        for key, expected in {
            'id': 'day015', 'slug': 'doh-watcher', 'title': 'DoH Watcher',
            'repo_url': 'https://github.com/ipusiron/doh-watcher',
            'demo_url': 'https://colab.research.google.com/github/ipusiron/doh-watcher/blob/main/doh_watcher.ipynb',
            'hub': 'true', 'difficulty': '2',
        }.items():
            actual = re.search(r'^' + key + r':\s*(.+)$', metadata, re.M).group(1).strip('"')
            self.assertEqual(actual, expected)
        for key, values in [('category_ja', ['ネットワーク']), ('category_en', ['Network']),
                            ('tags', ['dns', 'doh', 'privacy', 'network', 'colab'])]:
            block = re.search(r'^' + key + r':\n((?:  - .+\n?)+)', metadata, re.M)
            self.assertIsNotNone(block)
            self.assertEqual(re.findall(r'^  - (.+)$', block.group(1), re.M), values)

    def test_images_and_badges(self):
        images = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', README)
        self.assertEqual(len(images), 9)
        local = [name for name in images if not name.startswith('https://')]
        self.assertEqual(local, ['images/screenshot1.png', 'assets/screenshot.png',
                                 'assets/screenshot2.png', 'assets/screenshot3.png'])
        for name in local:
            self.assertTrue((ROOT / name).is_file(), name)
        self.assertTrue((ROOT / 'images/screenshot2.png').is_file())
        for name in local[1:]:
            data = (ROOT / name).read_bytes()
            self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
            self.assertEqual(struct.unpack('!II', data[16:24]), (1200, 720))
            self.assertLessEqual(len(data), 300_000)

    def test_package_list_matches_imports(self):
        section = re.search(r'^## 📦 使用ライブラリー\n(.*?)(?=^## )', README, re.M | re.S).group(1)
        listed = re.findall(r'^- `([^`]+)`', section, re.M)
        self.assertEqual(len(listed), 3)
        imported = set()
        for cell in notebook()['cells']:
            if cell['cell_type'] != 'code':
                continue
            for node in ast.walk(ast.parse(''.join(cell['source']))):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split('.')[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imported.add(node.module.split('.')[0])
        self.assertEqual(set(listed), imported - sys.stdlib_module_names)
        self.assertEqual(set(listed), {'requests', 'pandas', 'matplotlib'})

    def test_spelling_and_sections(self):
        self.assertNotIn('Claudeflare', README)
        self.assertNotIn('早い', README)
        self.assertIn('**Day015 - 生成AIで作るセキュリティツール100**', README)
        self.assertNotIn('Day15', README)
        headings = re.findall(r'^## .+$', README, re.M)
        self.assertGreaterEqual(len(headings), 14)
        self.assertEqual(headings[:2], ['## 🌐 デモページ', '## 📸 スクリーンショット'])
        self.assertEqual(headings[-5:], ['## 📁 ディレクトリー構造', '## 🧪 テスト',
                                        '## 💻 動作環境', '## 📄 ライセンス', '## 🛠️ このツールについて'])
        self.assertFalse(re.search(r'^#+ .*：$', README, re.M))
        self.assertIn('page_id=42163', README)

    def test_directory_tree_and_cell_documentation(self):
        tree = re.search(r'## 📁 ディレクトリー構造\s+```text\n(.*?)```', README, re.S).group(1)
        paths = []
        stack = []
        for line in tree.splitlines()[1:]:
            match = re.match(r'((?:│   |    )*)(?:├── |└── )(.+)', line)
            self.assertIsNotNone(match, line)
            depth = len(match.group(1)) // 4
            stack = stack[:depth]
            name = match.group(2).rstrip('/')
            paths.append('/'.join(stack + [name]))
            if match.group(2).endswith('/'):
                stack.append(name)
        self.assertEqual(paths, [
            '.github', '.github/workflows', '.github/workflows/test.yml',
            'assets', 'assets/screenshot.png', 'assets/screenshot2.png', 'assets/screenshot3.png',
            'images', 'images/screenshot1.png', 'images/screenshot2.png',
            'tests', 'tests/nbloader.py', 'tests/test_notebook.py', 'tests/test_readme.py',
            'tests/test_stats.py', 'tests/test_transport.py', 'tests/test_wireformat.py',
            '.gitignore', 'CLAUDE.md', 'doh_watcher.ipynb', 'LICENSE', 'README.md',
        ])
        for path in paths:
            self.assertTrue((ROOT / path).exists(), path)
        guide = (ROOT / 'CLAUDE.md').read_text(encoding='utf-8')
        for cell in notebook()['cells']:
            self.assertIn(cell['id'], guide)
