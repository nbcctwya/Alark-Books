"""Publication gates and report provenance, using isolated manuscript fixtures."""
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
import json
import shutil
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
import pymupdf as fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from alark_publishing import cli
from alark_publishing.manuscript import BookError

class BuildTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='alark-build-test-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        shutil.copy(cli.ROOT / 'publishing.yml', self.root)
        self.book = self.root / 'vault/books/sample'
        self.book.mkdir(parents=True)
        (self.book / 'book.yml').write_text('title: "测试 & 样书"\nchapters: [a.md]\n')
        (self.book / 'a.md').write_text('# 第一章\n\n正文。\n')
        fonts = self.root / 'design/fonts'
        fonts.mkdir(parents=True)
        for family in ['Serif', 'Sans']:
            (fonts / f'Noto{family}SC-Regular.ttf').write_bytes(b'fixture')
        brand = self.root / 'design/brand'
        brand.mkdir()
        (brand / 'mark.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        for target, value in [('alark_publishing.cli.ROOT', self.root), ('alark_publishing.cli.VAULT', self.root / 'vault'), ('alark_publishing.manuscript.VAULT', self.root / 'vault')]:
            p = patch(target, value)
            p.start()
            self.addCleanup(p.stop)
        pdf = fitz.open()
        pdf.new_page()
        document = Mock(pages=[])
        document.copy.return_value.write_pdf.return_value = pdf.tobytes()
        pdf.close()
        p = patch.object(cli, 'render_html', return_value=document)
        self.renderer = p.start()
        self.addCleanup(p.stop)
        self.output = self.root / 'exports/sample'

    def build(self, formats, formal=False):
        with redirect_stdout(StringIO()):
            cli.build_one('sample', ['portrait'], formats, formal)

    def seed(self):
        self.output.mkdir(parents=True)
        for name in ['sample.epub', 'epubcheck.json', 'sample.epubcheck.json']:
            (self.output / name).write_bytes(b'previous edition')

    def epub(self, errors=()):
        def write(manuscript, metadata, stage, output):
            output.write_bytes(b'new edition')
        return patch.object(cli, 'write_epub', side_effect=write), patch.object(cli, 'check_epub', return_value={'kind':'epub', 'file':'sample.epub', 'chapters':1, 'errors':list(errors), 'warnings':[]})

    def test_html_only_book_appears_without_cover_or_renderer(self):
        self.build(['html'])
        cli.build_library()
        self.renderer.assert_not_called()
        index = (self.root / 'exports/index.html').read_text()
        self.assertIn('sample/sample-portrait.html', index)
        self.assertIn('测试 &amp; 样书', index)
        self.assertNotIn('sample/cover.png', index)
        self.assertNotIn('longform-review/index.html', index)

    def test_all_html_profiles_are_discoverable(self):
        for profile in ['portrait', 'landscape', 'a4']:
            with self.subTest(profile=profile), redirect_stdout(StringIO()):
                if self.output.exists():
                    shutil.rmtree(self.output)
                cli.build_one('sample', [profile], ['html'])
                cli.build_library()
                index = (self.root / 'exports/index.html').read_text()
                self.assertIn(f'sample/sample-{profile}.html', index)
        self.renderer.assert_not_called()

    def test_unbuilt_invalid_draft_does_not_break_library(self):
        self.build(['html'])
        draft = self.root / 'vault/books/draft'
        draft.mkdir()
        (draft / 'book.yml').write_text('title: [unfinished')
        cli.build_library()
        self.assertIn('sample/sample-portrait.html', (self.root / 'exports/index.html').read_text())

    def test_invalid_metadata_keeps_existing_downloads_with_warning(self):
        self.build(['html'])
        for source in ['title: [unfinished', '[]', 'title: 123', 'title: sample\nsubtitle: []']:
            with self.subTest(source=source), redirect_stderr(StringIO()) as warning:
                (self.book / 'book.yml').write_text(source)
                cli.build_library()
                self.assertIn('sample/sample-portrait.html', (self.root / 'exports/index.html').read_text())
                self.assertIn('sample', warning.getvalue())

    def test_rebuilt_epub_removes_previous_validation_reports(self):
        self.seed()
        writer, checker = self.epub()
        with writer, checker:
            self.build(['epub'])
        self.assertEqual((self.output / 'sample.epub').read_bytes(), b'new edition')
        for name in ['epubcheck.json', 'sample.epubcheck.json']:
            self.assertFalse((self.output / name).exists())
        report = json.loads((self.output / 'checks.json').read_text())
        self.assertEqual(report['artifacts'][0]['epubcheck_status'], 'not_run')

    def test_formal_validation_replaces_report(self):
        self.seed()
        def validate(epub, report):
            report.write_text('{"new": true}')
            return 0, 'passed'
        writer, checker = self.epub()
        with writer, checker, patch('alark_publishing.epubcheck.validate', side_effect=validate):
            self.build(['epub'], True)
        self.assertEqual(json.loads((self.output / 'epubcheck.json').read_text()), {'new':True})
        self.assertFalse((self.output / 'sample.epubcheck.json').exists())
        report = json.loads((self.output / 'checks.json').read_text())
        self.assertEqual(report['artifacts'][0]['epubcheck_status'], 'passed')

    def test_epub_omits_empty_optional_metadata(self):
        import zipfile
        from lxml import etree
        with patch('alark_publishing.epub.subset_font', return_value=b'font fixture'):
            self.build(['epub'])
        with zipfile.ZipFile(self.output / 'sample.epub') as archive:
            package = etree.fromstring(archive.read('EPUB/package.opf'))
        ns = {'dc':'http://purl.org/dc/elements/1.1/'}
        self.assertEqual(package.xpath('//dc:description', namespaces=ns), [])
        self.assertEqual(package.xpath('//dc:title/text()', namespaces=ns), ['测试 & 样书'])

    def test_spectacle_keeps_distinct_intros_and_deduplicates_equal_ones(self):
        import zipfile
        from lxml import etree, html
        (self.book / 'book.yml').write_text('title: 测试\ndesign: spectacle\nchapters: [a.md]\n')
        for subtitle in ['同一条引导语', '另一条引导语']:
            with self.subTest(subtitle=subtitle), patch('alark_publishing.epub.subset_font', return_value=b'font fixture'):
                (self.book / 'a.md').write_text(f'---\nsubtitle: {subtitle}\nstatement: 同一条引导语\n---\n# 第一章\n\n独立正文。')
                self.build(['html', 'epub'])
                page = html.fromstring((self.output / 'sample-portrait.html').read_text())
                opener = page.xpath('//*[contains(@class,"campaign-opener")]')[0]
                self.assertEqual(opener.text_content().count('同一条引导语'), 1)
                with zipfile.ZipFile(self.output / 'sample.epub') as archive:
                    chapter = etree.fromstring(archive.read('EPUB/ch-01.xhtml'))
                text = ''.join(chapter.itertext())
                self.assertEqual(text.count('同一条引导语'), 1)
                self.assertIn(subtitle, text)
                self.assertIn('独立正文。', text)

    def test_failed_build_preserves_previous_edition_and_reports(self):
        self.seed()
        before = {p.name:p.read_bytes() for p in self.output.iterdir()}
        writer, checker = self.epub(['broken internal link'])
        with writer, checker, self.assertRaises(BookError):
            self.build(['epub'])
        self.assertEqual(before, {p.name:p.read_bytes() for p in self.output.iterdir()})
        self.assertTrue((self.root / 'exports/sample-failed-checks.json').exists())

if __name__ == '__main__':
    unittest.main()
