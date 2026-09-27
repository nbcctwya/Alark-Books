"""Obsidian Markdown -> semantic, linked HTML shared by all renderers."""
from __future__ import annotations
import hashlib
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
from html import escape
import yaml
from PIL import Image
from lxml import html, etree
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin

ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / 'vault'

class BookError(ValueError):
    pass

def read_markdown(path):
    text = path.read_text(encoding='utf-8').replace('\r\n', '\n')
    meta = {}
    if text.startswith('---\n'):
        parts = text.split('\n---', 1)
        if len(parts) != 2:
            raise BookError(f'未闭合的 YAML: {path}')
        meta = yaml.safe_load(parts[0][4:]) or {}
        text = parts[1].lstrip('\n')
    if not isinstance(meta, dict):
        raise BookError(f'章节 YAML 必须是映射: {path}')
    return meta, re.sub(r'%%.*?%%', '', text, flags=re.S)

def slug(text):
    return re.sub(r'[^\w\-\u3400-\u9fff]+', '-', text.strip().lower()).strip('-') or 'section'

def within(path, parent):
    return path.resolve().is_relative_to(parent.resolve())

def resolve_file(ref, chapter, assets_only=False):
    ref = unquote(ref).replace('\\', '/')
    roots = [chapter.parent, VAULT, VAULT / 'assets']
    matches = { (root / ref).resolve() for root in roots if (root / ref).is_file() and within(root / ref, VAULT) }
    if not matches:
        matches = {p.resolve() for p in VAULT.rglob(Path(ref).name) if p.is_file() and within(p, VAULT)}
    if len(matches) != 1:
        raise BookError(f'{chapter.name}: 文件不存在或重名，请使用明确路径: {ref}')
    result = matches.pop()
    if assets_only and not within(result, VAULT / 'assets'):
        raise BookError(f'图片请放入 vault/assets: {ref}')
    return result

def wiki_plugin(md):
    def rule(state, silent):
        match = re.match(r'(!?)\[\[([^\]\n]+)\]\]', state.src[state.pos:])
        if not match:
            return False
        embed, inner = match.groups()
        target, _, label = inner.partition('|')
        if embed and Path(target).suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif'}:
            raise BookError(f'暂不支持笔记嵌入，请改成链接: {target}')
        if not silent:
            if embed:
                token = state.push('image', 'img', 0)
                token.attrSet('src', quote(target, safe='/#'))
                if re.fullmatch(r'\d+(?:x\d+)?', label):
                    token.attrSet('title', 'width:' + label.split('x')[0])
                    label = ''
                token.content = label or Path(target).stem
                child = state.push('text', '', 0)
                state.tokens.pop()
                child.content = token.content
                token.children = [child]
                token.attrSet('alt', token.content)
            else:
                token = state.push('link_open', 'a', 1)
                token.attrSet('href', quote(target, safe='/#'))
                state.push('text', '', 0).content = label or target
                state.push('link_close', 'a', -1)
        state.pos += match.end()
        return True
    md.inline.ruler.before('link', 'obsidian_wiki', rule)


class Manuscript:
    def __init__(self, directory):
        self.directory = directory.resolve()
        config = directory / 'book.yml'
        if not config.exists():
            raise BookError(f'缺少 {config}；用 init 创建书籍配置。')
        self.meta = yaml.safe_load(config.read_text(encoding='utf-8'))
        if not isinstance(self.meta, dict) or not self.meta.get('title'):
            raise BookError('book.yml 必须包含 title')
        self.assets = {}
        self.chapters = []
        files = self.meta.get('chapters')
        if not isinstance(files, list) or not files:
            raise BookError('chapters 必须明确列出非空的章节顺序')
        parser = MarkdownIt('commonmark', {'html': False, 'typographer': True}).enable(['table', 'strikethrough']).use(footnote_plugin).use(wiki_plugin)
        seen = set()
        for index, filename in enumerate(files, 1):
            path = (directory / filename).resolve()
            if not within(path, directory) or not path.is_file() or path in seen:
                raise BookError(f'无效、重复或越界章节: {filename}')
            seen.add(path)
            metadata, source = read_markdown(path)
            if not source.strip():
                raise BookError(f'空章节: {filename}')
            document = html.fragment_fromstring(parser.render(source), create_parent='div')
            first = document.find('h1')
            title = metadata.get('title') or (first.text_content() if first is not None else path.stem)
            if first is not None:
                document.remove(first)
            cid = f'ch-{index:02d}'
            headings = {slug(title): cid}
            used = set()
            for heading in document.xpath('.//h1|.//h2|.//h3|.//h4|.//h5|.//h6'):
                base = slug(heading.text_content())
                key, n = base, 1
                while key in used:
                    n += 1
                    key = f'{base}-{n}'
                used.add(key)
                heading.set('id', key)
                headings.setdefault(base, f'{cid}-{key}')
            ids = {element.get('id'): f'{cid}-{element.get("id")}' for element in document.xpath('.//*[@id]')}
            for element in document.xpath('.//*[@id]'):
                element.set('id', ids[element.get('id')])
            for anchor in document.xpath('.//a[starts-with(@href, "#")]'):
                old = anchor.get('href')[1:]
                if old in ids:
                    anchor.set('href', '#' + ids[old])
            for block in document.xpath('.//blockquote'):
                paragraph = block.find('p')
                if paragraph is not None and paragraph.text:
                    callout = re.match(r'^\[!([\w-]+)\][+-]?\s*([^\n]*)(?:\n|$)', paragraph.text)
                    if callout:
                        kind, label = callout.groups()
                        block.tag = 'aside'
                        block.set('class', 'callout ' + slug(kind))
                        paragraph.text = paragraph.text[callout.end():]
                        heading = etree.Element('p', {'class': 'callout-title'})
                        heading.text = label or {'note':'旁注', 'tip':'行动建议', 'warning':'注意', 'quote':'摘记', 'important':'关键判断'}.get(kind.lower(), '提示')
                        block.insert(0, heading)
            for image in document.xpath('.//img'):
                src = image.get('src', '')
                if urlsplit(src).scheme or src.startswith('//'):
                    raise BookError(f'{filename}: 请先下载远程图片到 vault/assets: {src}')
                path_image = resolve_file(src, path, assets_only=True)
                if path_image.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg'}:
                    raise BookError(f'不支持的图片格式: {src}')
                asset_name = hashlib.sha256(path_image.read_bytes()).hexdigest()[:16] + path_image.suffix.lower()
                self.assets[asset_name] = path_image
                image.set('src', 'assets/' + asset_name)
                title_attr = image.get('title', '')
                if title_attr.startswith('width:'):
                    width = min(max(int(title_attr[6:]), 24), 1800)
                    image.set('style', f'width: {width}px; max-width: 100%')
                    image.attrib.pop('title', None)
                parent = image.getparent()
                if parent.tag == 'p' and len(parent) == 1 and not (parent.text or '').strip() and not (image.tail or '').strip():
                    parent.tag = 'figure'
                    if path_image.suffix.lower() != '.svg':
                        with Image.open(path_image) as info:
                            if info.height > info.width * 1.4:
                                parent.set('class', 'figure-tall')
                    if image.get('alt'):
                        etree.SubElement(parent, 'figcaption').text = image.get('alt')
            for table in document.xpath('.//table'):
                first_header = table.find('./thead/tr/th')
                if first_header is not None and first_header.text_content() in {'记录', '序号', '编号'}:
                    table.set('class', 'record-table')
            self.chapters.append(dict(id=cid, number=f'{index:02d}', title=str(title), subtitle=str(metadata.get('subtitle', '')), kicker=str(metadata.get('kicker', 'CHAPTER')), statement=str(metadata.get('statement', '')), document=document, path=path, headings=headings))
        self._link_chapters()

    def _link_chapters(self):
        path_map = {c['path']: c for c in self.chapters}
        all_ids = {c['id'] for c in self.chapters}
        for chapter in self.chapters:
            all_ids.update(e.get('id') for e in chapter['document'].xpath('.//*[@id]'))
        for chapter in self.chapters:
            for anchor in chapter['document'].xpath('.//a[@href]'):
                href = unquote(anchor.get('href'))
                parts = urlsplit(href)
                if parts.scheme in {'http', 'https', 'mailto'}:
                    continue
                if parts.scheme or parts.netloc:
                    raise BookError(f'不支持的链接: {href}')
                if not parts.path and parts.fragment in all_ids:
                    continue
                target = chapter
                if parts.path:
                    ref = parts.path if Path(parts.path).suffix else parts.path + '.md'
                    target_path = resolve_file(ref, chapter['path'])
                    if target_path not in path_map:
                        raise BookError(f'链接指向未收入本书的章节: {href}')
                    target = path_map[target_path]
                dest = target['id']
                if parts.fragment:
                    dest = target['headings'].get(slug(parts.fragment))
                    if not dest:
                        raise BookError(f'找不到章节标题: {href}')
                anchor.set('href', '#' + dest)
            chapter['html'] = ''.join(html.tostring(e, encoding='unicode') for e in chapter['document'])

    @property
    def text(self):
        return str(self.meta) + ''.join(c['title'] + c['document'].text_content() for c in self.chapters)
