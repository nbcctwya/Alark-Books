"""Regression coverage for content preservation and exported navigation."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from alark_publishing.manuscript import Manuscript, BookError
from alark_publishing.paths import ROOT, STYLES, TEMPLATES
from alark_publishing.themes import THEMES
from alark_publishing.preflight import check_epub

class ManuscriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='alark-test-')
        self.addCleanup(self.temp.cleanup)
        self.vault = Path(self.temp.name) / 'vault'
        self.directory = self.vault / 'books' / 'sample'
        self.directory.mkdir(parents=True)
        assets = self.vault / 'assets' / 'fixture'
        assets.mkdir(parents=True)
        Image.new('RGB', (32, 32), 'white').save(assets / 'diagram.png')
        patcher = patch('alark_publishing.manuscript.VAULT', self.vault)
        patcher.start()
        self.addCleanup(patcher.stop)
    def book(self, chapters, **metadata):
        for name, text in chapters.items():
            (self.directory / name).write_text(text, encoding='utf-8')
        (self.directory / 'book.yml').write_text(yaml.safe_dump({'title':'测试', 'chapters':list(chapters), **metadata}, allow_unicode=True), encoding='utf-8')
        return Manuscript(self.directory)
    def test_invalid_book_metadata_types_raise_book_error(self):
        for metadata in [{'title':123}, {'design':[]}, {'theme':{}}, {'author':[]}, {'cover_title_lines':'文字'}, {'manifesto_lines':[123]}]:
            with self.subTest(metadata=metadata), self.assertRaises(BookError):
                self.book({'a.md':'# 正文'}, **metadata)
        (self.directory / 'book.yml').write_text('title: test\nchapters: [123]\n')
        with self.assertRaises(BookError):
            Manuscript(self.directory)

    def test_invalid_chapter_metadata_types_raise_book_error(self):
        for field, value in [('title', 123), ('layout', []), ('photo_layout', {})]:
            with self.subTest(field=field), self.assertRaises(BookError):
                self.book({'a.md':'---\n'+yaml.safe_dump({field:value})+'---\n# 正文'})

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
    def test_wrong_explicit_image_path_does_not_fall_back_to_basename(self):
        with self.assertRaises(BookError):
            self.book({'a.md':'# 甲\n\n![[assets/wrong-folder/diagram.png]]'})
        m=self.book({'a.md':'# 甲\n\n![[diagram.png|允许无歧义的文件名]]'})
        self.assertEqual(len(m.assets),1)
    def test_wrong_explicit_chapter_path_does_not_fall_back_to_basename(self):
        with self.assertRaises(BookError):
            self.book({'a.md':'# 甲\n\n[[wrong-folder/b|错链]]','b.md':'# 乙\n\n正文。'})
    def test_missing_heading_fails(self):
        with self.assertRaises(BookError): self.book({'a.md':'# 甲\n\n[错链](#不存在)'})
    def test_chapter_escape_fails(self):
        (self.vault / 'outside.md').write_text('# Outside\n')
        (self.directory/'book.yml').write_text('title: test\nchapters: [../../outside.md]\n')
        with self.assertRaises(BookError): Manuscript(self.directory)
    def test_callout_formatting_and_picture_caption(self):
        m=self.book({'a.md':'# 甲\n\n> [!tip] 行动\n> 保留 **重点**。\n\n![[assets/fixture/diagram.png|流程说明]]\n'})
        self.assertIn('<aside',m.chapters[0]['html'])
        self.assertIn('<strong>重点</strong>',m.chapters[0]['html'])
        self.assertIn('<figcaption>流程说明</figcaption>',m.chapters[0]['html'])
    def test_chapter_density_is_validated(self):
        m=self.book({'a.md':'---\nlayout: dense\n---\n# 正文\n\n连续阅读。'})
        self.assertEqual(m.chapters[0]['layout'], 'dense')
        with self.assertRaises(BookError):
            self.book({'a.md':'---\nlayout: unknown\n---\n# 正文'})

    def test_editorial_endnotes_group_keeps_source_and_links(self):
        from alark_publishing.cli import editorial_chapters
        m=self.book({'a.md':'# 甲\n\n正文[^x]。\n\n> [!tip] 收尾\n> 最后一个行动。\n\n[^x]: 简短注释。'})
        original=m.chapters[0]['html']
        rendered=editorial_chapters(m.chapters)[0]['document']
        group=rendered.find("div[@class='chapter-notes']")
        self.assertIsNotNone(group)
        self.assertEqual([e.tag for e in group], ['aside', 'hr', 'section'])
        self.assertEqual(rendered.text_content(), m.chapters[0]['document'].text_content())
        self.assertEqual(rendered.xpath('.//a/@href'), m.chapters[0]['document'].xpath('.//a/@href'))
        self.assertEqual(m.chapters[0]['html'], original)
        long=self.book({'a.md':'# 甲\n\n正文[^x]。\n\n最后一段。\n\n[^x]: '+('长注释。'*100)})
        self.assertIsNone(editorial_chapters(long.chapters)[0]['document'].find("div[@class='chapter-notes']"))

    def test_short_and_long_tables_have_different_pagination(self):
        header='| 记录 | 内容 |\n| --- | --- |\n'
        short=header+'| 1 | 核对 |\n'
        long=header+''.join(f'| {i} | 记录 |\n' for i in range(20))
        m=self.book({'a.md':'# 表格\n\n'+short+'\n'+long})
        tables=m.chapters[0]['document'].xpath('.//table')
        self.assertIn('compact-table',tables[0].get('class'))
        self.assertNotIn('compact-table',tables[1].get('class'))
        self.assertIn('record-table',tables[1].get('class'))

    def test_duplicate_headings(self):
        m=self.book({'a.md':'# 甲\n\n## 重复\n\n一\n\n## 重复\n\n二'})
        ids=m.chapters[0]['document'].xpath('.//h2/@id')
        self.assertEqual(ids,['ch-01-重复','ch-01-重复-2'])

    def test_folio_groups_preserve_order_captions_and_text(self):
        photo=lambda caption: f'![[assets/fixture/diagram.png|{caption}]]\n\n'
        source='---\nphoto_layout: pair\n---\n# 图册\n\n'+photo('甲')+photo('乙')+photo('丙')+'中间的文字。\n\n'+photo('丁')+'[[b|后记]]'
        m=self.book({'a.md':source,'b.md':'# 后记\n\n结束。'},design='folio')
        doc=m.chapters[0]['document']
        self.assertEqual([len(g) for g in doc.xpath('./div[@class="folio-gallery"]')],[2,1,1])
        self.assertEqual(doc.xpath('.//figcaption/text()'),['甲','乙','丙','丁'])
        self.assertIn('中间的文字。',doc.text_content())
        self.assertEqual(doc.xpath('.//a/@href'),['#ch-02'])
        ordinary=self.book({'a.md':source,'b.md':'# 后记\n\n结束。'})
        self.assertEqual(len(ordinary.chapters[0]['document'].findall('figure')),4)

    def test_folio_bleed_rejects_content_that_would_be_hidden(self):
        src='---\nphoto_layout: bleed\n---\n# 满版\n\n![[assets/fixture/diagram.png|图注]]\n'
        m=self.book({'a.md':src},design='folio')
        self.assertEqual(m.chapters[0]['photo_layout'],'bleed')
        with self.assertRaises(BookError):
            self.book({'a.md':src+'\n不能被裁掉的正文。'},design='folio')
        with self.assertRaises(BookError):
            self.book({'a.md':'---\nphoto_layout: typo\n---\n# 甲'},design='folio')

    def test_folio_contact_sheet_splits_large_sets(self):
        src='---\nphoto_layout: contact\n---\n# 组照\n\n'+''.join(f'![[assets/fixture/diagram.png|图 {i}]]\n\n' for i in range(9))
        m=self.book({'a.md':src},design='folio')
        groups=m.chapters[0]['document'].xpath('./div[@class="folio-gallery"]')
        self.assertEqual([len(g) for g in groups],[4,4,1])
        self.assertEqual(len(m.chapters[0]['document'].xpath('.//img')),9)
    def test_image_cannot_escape_vault_assets(self):
        Image.new('RGB', (32, 32)).save(self.directory / 'private.png')
        with self.assertRaises(BookError):
            self.book({'a.md': '# 甲\n\n![[private.png]]'})

class ResourceTests(unittest.TestCase):
    def test_theme_resources_exist(self):
        for name, theme in THEMES.items():
            with self.subTest(theme=name):
                self.assertTrue((TEMPLATES / theme.template).is_file())
                for style in (*theme.styles, *((theme.epub_style,) if theme.epub_style else ())):
                    self.assertTrue((STYLES / style).is_file(), style)

    def test_exported_epubs_are_link_complete(self):
        found = 0
        for name in ['layout-lab', 'field-notes', 'desire-manufacture', 'business-architecture', 'through-volatility', 'shore-and-space']:
            path=ROOT / 'exports' / name / f'{name}.epub'
            if path.exists():
                found += 1
                with self.subTest(book=name): self.assertEqual(check_epub(path)['errors'], [])
        if not found:
            self.skipTest('尚未构建 EPUB；资源检查需先构建样书')

if __name__=='__main__': unittest.main()
