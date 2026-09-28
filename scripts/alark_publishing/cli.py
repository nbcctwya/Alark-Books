#!/usr/bin/env python
"""AIark / Alark publishing CLI. Run from any directory in the webproj environment."""
import argparse
import json
import logging
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from copy import deepcopy
from lxml import html, etree
import uuid
from urllib.parse import unquote, urlsplit
import pymupdf as fitz
from jinja2 import Environment, FileSystemLoader, select_autoescape
import yaml
from weasyprint import HTML, default_url_fetcher
from .manuscript import Manuscript, BookError, resolve_file
from .paths import ROOT, VAULT, STYLES, TEMPLATES
from .themes import THEMES
from .epub import write_epub
from .preflight import check_pdf, check_epub, contact_sheet


def config():
    return yaml.safe_load((ROOT / 'publishing.yml').read_text(encoding='utf-8'))


def safe_book(name):
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]*', name):
        raise BookError('书籍目录名只能包含字母、数字、连字符、下划线')
    path = VAULT / 'books' / name
    if not path.resolve().is_relative_to((VAULT / 'books').resolve()):
        raise BookError('书籍目录不可指向 vault/books 之外')
    return path


def init_book(name, title):
    directory = safe_book(name)
    if directory.exists():
        raise BookError(f'目录已存在，不覆盖：{directory}')
    directory.mkdir(parents=True)
    meta = dict(title=title or name, subtitle='在这里写下本书的副标题', author=config()['brand']['author'], language='zh-CN', identifier='urn:uuid:' + str(uuid.uuid4()), edition='第一版', theme='vermilion', chapters=['01-start.md'])
    (directory / 'book.yml').write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding='utf-8')
    (directory / '01-start.md').write_text('# 从这里开始\n\n写下这本书要回答的第一个问题。\n\n## 核心观点\n\n在 Obsidian 中开始写作。\n', encoding='utf-8')
    print(directory)


def profile_css(profile, name, theme, title):
    accent, tint = {'vermilion': ('#b44330', '#f1e8de'), 'forest': ('#28574f', '#e7eee6')}[theme]
    p = profile
    # CSS strings are JSON quoted to keep metadata from changing stylesheet syntax.
    title_css = json.dumps(title, ensure_ascii=False)
    return f''':root {{ --accent: {accent}; --tint: {tint}; --page-width: {p['width_mm']}mm; --page-height: {p['height_mm']}mm; --image-height: {p['height_mm']-p['margin_top_mm']-p['margin_bottom_mm']-24}mm; }}
body {{ font-size: {p['font_pt']}pt; }}
@page {{ size: {p['width_mm']}mm {p['height_mm']}mm; margin: {p['margin_top_mm']}mm {p['margin_outer_mm']}mm {p['margin_bottom_mm']}mm {p['margin_inner_mm']}mm; background: #fdfcf8;
 @top-left {{ content: none; }}
 @top-right {{ content: string(chapter-title); font: 7pt ArkSerif; color: #726e65; }}
 @bottom-left {{ content: none; }}
 @bottom-right {{ content: counter(page); font: 8pt ArkSerif; color: #292722; }} }}
@page :left {{ margin-left: {p['margin_outer_mm']}mm; margin-right: {p['margin_inner_mm']}mm;
 @top-left {{ content: {title_css}; font: 7pt ArkSerif; color: #726e65; }}
 @top-right {{ content: none; }}
 @bottom-left {{ content: counter(page); font: 8pt ArkSerif; color: #292722; }}
 @bottom-right {{ content: none; }} }}
@page cover {{ margin: 0; @top-left {{ content: none; }} @top-right {{ content: none; }} @bottom-left {{ content: none; }} @bottom-right {{ content: none; }} }}
'''


def art_svg(accent):
    paths = ''.join(f'<path d="M{65+i*9} 290 V145 A{110-i*3} {110-i*3} 0 0 1 {285-i*2} 145 V290"/>' for i in range(12))
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="420" height="340" viewBox="0 0 420 340"><g fill="none" stroke="{accent}" stroke-width="1.2">{paths}</g><path d="M30 290H380M90 315H330" stroke="#202a29" stroke-width="1"/><circle cx="285" cy="75" r="17" fill="{accent}"/></svg>'


def landscape_chapters(chapters):
    result = []
    for chapter in chapters:
        item = dict(chapter)
        root = etree.Element('div')
        flow = None
        for child in chapter['document']:
            child = deepcopy(child)
            if child.tag in {'figure', 'table', 'pre'} or child.get('class') == 'photo-essay':
                # Keep spanning content outside CSS columns; paged engines differ on column-span.
                if flow is not None and len(flow) and flow[-1].tag in {'h1', 'h2', 'h3'}:
                    root.append(flow[-1])
                if child.tag == 'figure' and flow is not None and len(flow) and flow[-1].tag == 'blockquote':
                    # Keep a pull quote with its photograph as one magazine plate.
                    plate = etree.SubElement(root, 'div', {'class': 'photo-essay'})
                    plate.append(flow[-1])
                    plate.append(child)
                else:
                    root.append(child)
                flow = None
            else:
                if flow is None:
                    flow = etree.SubElement(root, 'div', {'class': 'text-flow'})
                flow.append(child)
        item['html'] = ''.join(html.tostring(e, encoding='unicode') for e in root)
        result.append(item)
    return result


def editorial_chapters(chapters):
    """Keep short tables and adjacent quotation/photo plates intact."""
    result = []
    for chapter in chapters:
        item = dict(chapter)
        root = deepcopy(chapter['document'])
        for figure in list(root.findall('figure')):
            previous = figure.getprevious()
            if previous is not None and previous.tag == 'blockquote':
                plate = etree.Element('div', {'class': 'photo-essay'})
                root.insert(root.index(previous), plate)
                plate.append(previous)
                plate.append(figure)
        item['document'] = root
        item['html'] = ''.join(html.tostring(e, encoding='unicode') for e in root)
        result.append(item)
    return result


def build_one(name, profiles, formats, formal_check=False):
    settings = config()
    manuscript = Manuscript(safe_book(name))
    metadata = dict(manuscript.meta)
    brand = dict(settings['brand'])
    metadata.setdefault('author', brand['author'])
    metadata.setdefault('publisher', brand['name'])
    metadata.setdefault('identifier', 'urn:uuid:' + str(uuid.uuid5(uuid.NAMESPACE_URL, 'alark-books/' + name)))
    metadata.setdefault('subtitle', '')
    design = metadata.get('design', 'editorial')
    if design not in THEMES:
        raise BookError('design 只能是 ' + '、'.join(THEMES))
    theme = metadata.get('theme', 'vermilion')
    if theme not in {'vermilion', 'forest'}:
        raise BookError('theme 只能是 vermilion 或 forest')
    for family in ['Serif', 'Sans']:
        if not (ROOT / f'design/fonts/Noto{family}SC-Regular.ttf').exists():
            raise BookError('缺少字体，请先运行 python scripts/bootstrap_fonts.py')
    exports = ROOT / 'exports'
    exports.mkdir(exist_ok=True)
    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(['html', 'xml', 'j2']))
    template_name = THEMES[design].template
    template = env.get_template(template_name)
    destination = exports / name
    chapters = editorial_chapters(manuscript.chapters) if design == 'editorial' else manuscript.chapters
    reports = []
    # Stage the whole requested edition; publish only after every requested artifact succeeds.
    with tempfile.TemporaryDirectory(prefix=f'.{name}-', dir=exports) as temp:
        stage = Path(temp)
        if destination.exists():
            shutil.copytree(destination, stage, dirs_exist_ok=True)
        for folder in ['styles', 'fonts', 'assets', 'previews']:
            (stage / folder).mkdir(exist_ok=True)
        shutil.copy(STYLES / 'book.css', stage / 'styles/book.css')
        shutil.copy(STYLES / 'screen.css', stage / 'styles/screen.css')
        for style in THEMES[design].styles:
            shutil.copy(STYLES / style, stage / 'styles' / style)
        for file in (ROOT / 'design/fonts').glob('*'):
            if file.suffix in {'.ttf', '.txt'}:
                shutil.copy(file, stage / 'fonts' / file.name)
        shutil.copy(ROOT / 'design/brand/mark.svg', stage / 'assets/mark.svg')
        (stage / 'assets/orbit.svg').write_text(art_svg('#b44330' if theme == 'vermilion' else '#28574f'), encoding='utf-8')
        if metadata.get('cover_image'):
            cover_source = resolve_file(str(metadata['cover_image']), manuscript.directory / 'book.yml', assets_only=True)
            if cover_source.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.svg'}:
                raise BookError('封面图请使用 PNG、JPEG 或 SVG')
            metadata['cover_asset'] = 'assets/editorial-cover' + cover_source.suffix.lower()
            shutil.copy(cover_source, stage / metadata['cover_asset'])
        for filename, path in manuscript.assets.items():
            shutil.copy(path, stage / 'assets' / filename)
        def fetch(url, *args, **kwargs):
            parts = urlsplit(url)
            path = Path(unquote(parts.path)).resolve()
            if parts.scheme != 'file' or not path.is_relative_to(stage.resolve()):
                raise BookError(f'导出中禁止读取外部资源：{url}')
            return default_url_fetcher(url, *args, **kwargs)
        messages = []
        class Capture(logging.Handler):
            def emit(self, record):
                if record.levelno >= logging.WARNING:
                    messages.append(self.format(record))
        handler = Capture()
        logger = logging.getLogger('weasyprint')
        logger.addHandler(handler)
        try:
            for profile_name in profiles:
                profile = settings['profiles'][profile_name]
                rendered = template.render(book=metadata, brand=brand, profile=profile, profile_name=profile_name, chapters=landscape_chapters(chapters) if profile_name == 'landscape' and THEMES[design].landscape_columns else chapters)
                css_name = f'{profile_name}.css'
                (stage / 'styles' / css_name).write_text(profile_css(profile, profile_name, theme, metadata['title']), encoding='utf-8')
                rendered = rendered.replace('styles/profile.css', 'styles/' + css_name)
                html_path = stage / f'{name}-{profile_name}.html'
                html_path.write_text(rendered, encoding='utf-8')
                need_render = 'pdf' in formats or ('epub' in formats and profile_name == profiles[0])
                if need_render:
                    print(f'排版 {name} / {profile_name}', flush=True)
                    document = HTML(filename=html_path, url_fetcher=fetch).render()
                    layout_errors = []
                    for page_number, page in enumerate(document.pages, 1):
                        pagebox = page._page_box
                        for box in pagebox.descendants():
                            # Text bounds detect long unbreakable lines / too-wide tables.
                            if type(box).__name__ == 'TextBox' and not page_number == 1:
                                if box.position_x < -1 or box.position_x + box.width > page.width + 1:
                                    layout_errors.append(f'Page {page_number}: text overflows page')
                    if profile_name == profiles[0]:
                        cover_bytes = document.copy(document.pages[:1]).write_pdf()
                        with fitz.open(stream=cover_bytes, filetype='pdf') as cover_doc:
                            cover_doc[0].get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False).save(stage / 'cover.png')
                    if 'pdf' in formats:
                        pdf_path = stage / f'{name}-{profile_name}.pdf'
                        document.write_pdf(pdf_path)
                        report = check_pdf(pdf_path, (profile['width_mm'], profile['height_mm']))
                        report['errors'].extend(layout_errors)
                        reports.append(report)
                        contact_sheet(pdf_path, stage / 'previews' / f'{profile_name}-contact.png')
                if 'html' not in formats:
                    html_path.unlink()
            if 'epub' in formats:
                output = stage / f'{name}.epub'
                write_epub(manuscript, metadata, stage, output)
                reports.append(check_epub(output))
                if formal_check:
                    from .epubcheck import validate
                    code, result = validate(output, stage / 'epubcheck.json')
                    reports[-1]['epubcheck'] = result
                    if code:
                        reports[-1]['errors'].append(result)
        finally:
            logger.removeHandler(handler)
        failures = [error for report in reports for error in report['errors']]
        failures.extend(message for message in messages if 'Failed to load' in message)
        report_data = {'book': name, 'profiles': profiles, 'formats': formats, 'renderer_warnings': sorted(set(messages)), 'artifacts': reports}
        if failures:
            (exports / f'{name}-failed-checks.json').write_text(json.dumps(report_data, ensure_ascii=False, indent=2), encoding='utf-8')
            raise BookError('导出检查未通过：' + '; '.join(failures[:8]))
        (stage / 'checks.json').write_text(json.dumps(report_data, ensure_ascii=False, indent=2), encoding='utf-8')
        destination.mkdir(exist_ok=True)
        shutil.copytree(stage, destination, dirs_exist_ok=True)
        (exports / f'{name}-failed-checks.json').unlink(missing_ok=True)
    for report in reports:
        print(f'  {report["file"]}: {report.get("page_count", report.get("chapters"))} {"页" if report["kind"] == "pdf" else "章"}，{len(report["warnings"])} 项提醒')
    print(f'完成：{destination}')


def build_library():
    settings = config()
    books = []
    for path in sorted((VAULT / 'books').glob('*/book.yml')):
        slug = path.parent.name
        folder = ROOT / 'exports' / slug
        if not (folder / 'cover.png').exists():
            continue
        meta = yaml.safe_load(path.read_text(encoding='utf-8'))
        links = []
        for profile, label in [('portrait', '竖版 PDF'), ('landscape', '横版 PDF'), ('a4', 'A4 手册')]:
            filename = f'{slug}-{profile}.pdf'
            if (folder / filename).exists():
                links.append(dict(href=f'{slug}/{filename}', label=label))
        for filename, label in [(f'{slug}.epub', 'EPUB'), (f'{slug}-portrait.html', '在线阅读')]:
            if (folder / filename).exists():
                links.append(dict(href=f'{slug}/{filename}', label=label))
        if links:
            books.append(dict(slug=slug, volume=str(meta.get('volume', '01')), title=meta['title'], subtitle=meta.get('subtitle',''), series=meta.get('series', 'ALARK LIBRARY'), primary=links[0]['href'], links=links))
    books.sort(key=lambda book: (book['volume'], book['slug']))
    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=True)
    (ROOT / 'exports/index.html').write_text(env.get_template('library.html.j2').render(brand=settings['brand'], books=books), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='AIark / Alark 书籍出版工具')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list', help='列出书籍及配置状态')
    init = sub.add_parser('init', help='新建书籍，不覆盖已有目录')
    init.add_argument('book')
    init.add_argument('--title')
    build = sub.add_parser('build', help='生成 PDF、EPUB 和 HTML')
    build.add_argument('book', nargs='?')
    build.add_argument('--epubcheck', action='store_true', help='用本地 EPUBCheck 正式校验 EPUB')
    build.add_argument('--all', action='store_true', help='构建所有配置了 book.yml 的书籍')
    build.add_argument('--profile', default='portrait', choices=[*config()['profiles'], 'all'])
    build.add_argument('--format', default='all', choices=['all', 'pdf', 'epub', 'html'])
    check = sub.add_parser('check', help='检查已导出的 PDF 或 EPUB')
    check.add_argument('file', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'list':
            for directory in sorted((VAULT / 'books').iterdir()):
                if directory.is_dir():
                    print(f'{directory.name:24} {"已配置" if (directory / "book.yml").exists() else "尚未配置（不会自动构建）"}')
        elif args.command == 'init':
            init_book(args.book, args.title)
        elif args.command == 'check':
            result = check_epub(args.file) if args.file.suffix == '.epub' else check_pdf(args.file)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return bool(result['errors'])
        elif args.command == 'build':
            if bool(args.book) == bool(args.all):
                raise BookError('请指定书籍目录名，或使用 --all')
            names = [p.parent.name for p in sorted((VAULT / 'books').glob('*/book.yml'))] if args.all else [args.book]
            if not names:
                raise BookError('没有已配置的书籍')
            profiles = list(config()['profiles']) if args.profile == 'all' else [args.profile]
            formats = ['pdf', 'epub', 'html'] if args.format == 'all' else [args.format]
            if args.epubcheck and 'epub' not in formats:
                raise BookError('--epubcheck 需要 --format epub 或 --format all')
            for name in names:
                build_one(name, profiles, formats, args.epubcheck)
            build_library()
    except (BookError, OSError, yaml.YAMLError) as error:
        print(f'错误：{error}', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
