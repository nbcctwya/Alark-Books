"""Regression coverage for content preservation and exported navigation."""
from pathlib import Path
import sys
import tempfile
import unittest
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from manuscript import Manuscript, BookError, ROOT, VAULT
from preflight import check_epub

class ManuscriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='test-', dir=VAULT / 'books')
        self.directory = Path(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()
    def book(self, chapters):
        for name, text in chapters.items():
            (self.directory / name).write_text(text, encoding='utf-8')
        (self.directory / 'book.yml').write_text(yaml.safe_dump({'title':'测试', 'chapters':list(chapters)}, allow_unicode=True), encoding='utf-8')
        return Manuscript(self.directory)
    def test_footnotes_cross_chapter_and_unicode_anchors(self):
        m=self.book({'a.md':'# 甲\n\n正文[^x]。[[b#中文标题|下一节]]\n\n[^x]: 甲注释\n', 'b.md':'# 乙\n\n## 中文标题\n\n正文[^x]。\n\n[^x]: 乙注释\n'})
        ids=[e.get('id') for c in m.chapters for e in c['document'].xpath('.//*[@id]')]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertIn('#ch-02-中文标题', m.chapters[0]['document'].xpath('.//a/@href'))
        self.assertIn('ch-01-fn1', ids)
        self.assertIn('ch-02-fn1', ids)
    def test_wikilinks_in_code_are_literal(self):
        m=self.book({'a.md':'# 标题\n\n`[[missing]]`\n\n```text\n![[missing.png]]\n```\n'})
        self.assertIn('[[missing]]', m.chapters[0]['html'])
        self.assertIn('![[missing.png]]', m.chapters[0]['html'])
        self.assertFalse(m.assets)
    def test_missing_image_fails(self):
        with self.assertRaises(BookError): self.book({'a.md':'# 甲\n\n![[never-exists.png]]'})
    def test_missing_heading_fails(self):
        with self.assertRaises(BookError): self.book({'a.md':'# 甲\n\n[错链](#不存在)'})
    def test_chapter_escape_fails(self):
        (self.directory/'book.yml').write_text('title: test\nchapters: [../../principles/life-finds-a-way.md]\n')
        with self.assertRaises(BookError): Manuscript(self.directory)
    def test_callout_formatting_and_picture_caption(self):
        m=self.book({'a.md':'# 甲\n\n> [!tip] 行动\n> 保留 **重点**。\n\n![[assets/layout-lab/content-loop.png|流程说明]]\n'})
        self.assertIn('<aside',m.chapters[0]['html'])
        self.assertIn('<strong>重点</strong>',m.chapters[0]['html'])
        self.assertIn('<figcaption>流程说明</figcaption>',m.chapters[0]['html'])
    def test_duplicate_headings(self):
        m=self.book({'a.md':'# 甲\n\n## 重复\n\n一\n\n## 重复\n\n二'})
        ids=m.chapters[0]['document'].xpath('.//h2/@id')
        self.assertEqual(ids,['ch-01-重复','ch-01-重复-2'])
    def test_exported_epubs_are_link_complete(self):
        for name in ['layout-lab', 'field-notes', 'desire-manufacture', 'business-architecture', 'through-volatility']:
            path=ROOT / 'exports' / name / f'{name}.epub'
            if path.exists():
                with self.subTest(book=name): self.assertEqual(check_epub(path)['errors'], [])

if __name__=='__main__': unittest.main()
