"""EPUB 3 package with independent XHTML chapters, navigation and subset fonts."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import io
import mimetypes
from PIL import Image
import zipfile
from lxml import etree, html
from fontTools import subset
from fontTools.ttLib import TTFont

XHTML = 'http://www.w3.org/1999/xhtml'
EPUB = 'http://www.idpf.org/2007/ops'
OPF = 'http://www.idpf.org/2007/opf'
DC = 'http://purl.org/dc/elements/1.1/'
from .paths import ROOT, STYLES
from .themes import THEMES

def xhtml(title, body, language, body_class=None):
    root = etree.Element(f'{{{XHTML}}}html', nsmap={None: XHTML, 'epub': EPUB}, attrib={'lang': language, '{http://www.w3.org/XML/1998/namespace}lang': language})
    head = etree.SubElement(root, f'{{{XHTML}}}head')
    etree.SubElement(head, f'{{{XHTML}}}title').text = title
    etree.SubElement(head, f'{{{XHTML}}}link', rel='stylesheet', href='style.css', type='text/css')
    container = etree.SubElement(root, f'{{{XHTML}}}body')
    if body_class:
        container.set('class', body_class)
    for child in body:
        child = deepcopy(child)
        for element in child.iter():
            if isinstance(element.tag, str) and not element.tag.startswith('{'):
                element.tag = f'{{{XHTML}}}{element.tag}'
        container.append(child)
    return etree.tostring(root, encoding='utf-8', xml_declaration=True, doctype='<!DOCTYPE html>')

def subset_font(source, text):
    font = TTFont(source)
    options = subset.Options()
    options.name_IDs = ['*']
    options.name_legacy = True
    options.name_languages = ['*']
    cutter = subset.Subsetter(options=options)
    cutter.populate(text=text)
    cutter.subset(font)
    out = io.BytesIO()
    font.save(out)
    return out.getvalue()

def write_epub(manuscript, metadata, stage, output):
    language = metadata.get('language', 'zh-CN')
    resources = {}
    manifest = []
    spine = []
    def add(name, data, mime, properties=''):
        iid = 'item-' + str(len(manifest) + 1)
        manifest.append((iid, name, mime, properties))
        resources[name] = data
        return iid
    css = (STYLES / 'epub.css').read_text(encoding='utf-8')
    if metadata.get('theme') == 'forest':
        css = css.replace('#b44330', '#28574f').replace('#93402e', '#28574f').replace('#f3eee5', '#e7eee6')
    design = THEMES[metadata.get('design', 'editorial')]
    if design.epub_style:
        css += '\n' + (STYLES / design.epub_style).read_text(encoding='utf-8')
    add('style.css', css.encode(), 'text/css')
    text = manuscript.text + ''.join(c['statement'] + c['kicker'] for c in manuscript.chapters) + str(metadata) + '目录作者版权关于本书'
    for family in ['Serif', 'Sans']:
        add(f'fonts/{family.lower()}.ttf', subset_font(ROOT / f'design/fonts/Noto{family}SC-Regular.ttf', text), 'font/ttf')
        add(f'fonts/OFL-{family}.txt', (ROOT / f'design/fonts/OFL-{family}.txt').read_bytes(), 'text/plain')
    asset_aliases = {}
    for name, path in manuscript.assets.items():
        if path.suffix.lower() == '.webp':
            converted = str(Path(name).with_suffix('.png'))
            data = io.BytesIO()
            with Image.open(path) as im:
                im.save(data, format='PNG')
            add('assets/' + converted, data.getvalue(), 'image/png')
            asset_aliases['assets/' + name] = 'assets/' + converted
        else:
            add('assets/' + name, path.read_bytes(), mimetypes.guess_type(name)[0] or 'application/octet-stream')
    add('cover.png', (stage / 'cover.png').read_bytes(), 'image/png', 'cover-image')
    cover = etree.Element('section', {'id': 'cover'})
    etree.SubElement(cover, 'img', src='cover.png', alt=metadata['title'] + ' — ' + metadata.get('subtitle', ''))
    spine.append(add('cover.xhtml', xhtml(metadata['title'], [cover], language, 'cover-page'), 'application/xhtml+xml'))
    about = etree.Element('section', {'id': 'about'})
    etree.SubElement(about, 'h1').text = metadata['title']
    for value in [metadata.get('subtitle'), '作者：' + metadata['author'], metadata.get('description'), metadata.get('edition'), str(metadata.get('date', '')), metadata.get('rights', '版权所有。'), metadata.get('note'), ('封面图像：' + metadata['cover_credit']) if metadata.get('cover_credit') else None]:
        if value:
            etree.SubElement(about, 'p').text = str(value)
    if metadata.get('design') == 'spectacle':
        for line in metadata.get('manifesto_lines', []):
            etree.SubElement(about, 'p', {'class': 'campaign-epub-statement'}).text = str(line)
        etree.SubElement(about, 'p', {'class': 'eyebrow'}).text = metadata.get('manifesto_caption', '')
    spine.append(add('about.xhtml', xhtml('关于本书', [about], language), 'application/xhtml+xml'))
    nav = etree.Element('nav', {f'{{{EPUB}}}type': 'toc', 'id': 'toc'})
    etree.SubElement(nav, 'h1').text = '目录'
    ol = etree.SubElement(nav, 'ol')
    targets = {}
    for chapter in manuscript.chapters:
        filename = chapter['id'] + '.xhtml'
        targets[chapter['id']] = filename
        for element in chapter['document'].xpath('.//*[@id]'):
            targets[element.get('id')] = filename
        li = etree.SubElement(ol, 'li')
        etree.SubElement(li, 'a', href=filename + '#' + chapter['id']).text = chapter['number'] + ' ' + chapter['title']
        subheadings = chapter['document'].xpath('./h2')
        if subheadings:
            sub = etree.SubElement(li, 'ol')
            for heading in subheadings:
                etree.SubElement(etree.SubElement(sub, 'li'), 'a', href=filename + '#' + heading.get('id')).text = heading.text_content()
    spine.append(add('nav.xhtml', xhtml('目录', [nav], language), 'application/xhtml+xml', 'nav'))
    for chapter in manuscript.chapters:
        section = etree.Element('section', {'id': chapter['id'], f'{{{EPUB}}}type': 'chapter'})
        if metadata.get('design') == 'folio':
            section.set('class', 'folio-layout-' + chapter['photo_layout'])
        etree.SubElement(section, 'p', {'class': 'eyebrow'}).text = 'CHAPTER ' + chapter['number']
        etree.SubElement(section, 'h1').text = chapter['title']
        if chapter['subtitle']:
            etree.SubElement(section, 'p').text = chapter['subtitle']
        if metadata.get('design') == 'spectacle' and chapter['statement']:
            etree.SubElement(section, 'p', {'class': 'campaign-epub-statement'}).text = chapter['statement']
        if metadata.get('design') in {'business', 'investment'} and chapter['statement']:
            etree.SubElement(section, 'p', {'class': 'design-statement'}).text = chapter['statement']
        for child in chapter['document']:
            section.append(deepcopy(child))
        if metadata.get('design') == 'spectacle' and chapter is manuscript.chapters[-1]:
            for line in metadata.get('end_lines', []):
                etree.SubElement(section, 'p', {'class': 'campaign-epub-statement'}).text = str(line)
        for anchor in section.xpath('.//a[starts-with(@href, "#")]'):
            dest = anchor.get('href')[1:]
            anchor.set('href', targets[dest] + '#' + dest)
        for element in section.xpath('.//*[@class="footnote-ref"]/a'):
            element.set(f'{{{EPUB}}}type', 'noteref')
        for element in section.xpath('.//li[@class="footnote-item"]'):
            element.set(f'{{{EPUB}}}type', 'endnote')
        for element in section.xpath('.//img[@src]'):
            if element.get('src') in asset_aliases:
                element.set('src', asset_aliases[element.get('src')])
        props = ''
        spine.append(add(chapter['id'] + '.xhtml', xhtml(chapter['title'], [section], language), 'application/xhtml+xml', props))
    package = etree.Element(f'{{{OPF}}}package', nsmap={None: OPF, 'dc': DC}, attrib={'version': '3.0', 'unique-identifier': 'book-id', 'prefix': 'rendition: http://www.idpf.org/vocab/rendition/#'})
    meta = etree.SubElement(package, f'{{{OPF}}}metadata')
    for tag, value in [('identifier', metadata['identifier']), ('title', metadata['title']), ('language', language), ('creator', metadata['author']), ('publisher', metadata['publisher']), ('rights', metadata.get('rights', '版权所有。')), ('description', metadata.get('description', metadata.get('subtitle', '')))]:
        item = etree.SubElement(meta, f'{{{DC}}}{tag}')
        item.text = str(value)
        if tag == 'identifier':
            item.set('id', 'book-id')
    etree.SubElement(meta, f'{{{OPF}}}meta', property='dcterms:modified').text = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    etree.SubElement(meta, f'{{{OPF}}}meta', property='rendition:layout').text = 'reflowable'
    man = etree.SubElement(package, f'{{{OPF}}}manifest')
    for iid, name, mime, props in manifest:
        el = etree.SubElement(man, f'{{{OPF}}}item', id=iid, href=name, attrib={'media-type': mime})
        if props:
            el.set('properties', props)
    seq = etree.SubElement(package, f'{{{OPF}}}spine')
    for iid in spine:
        etree.SubElement(seq, f'{{{OPF}}}itemref', idref=iid)
    container = b'<?xml version="1.0" encoding="UTF-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="EPUB/package.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('mimetype', b'application/epub+zip', compress_type=zipfile.ZIP_STORED)
        archive.writestr('META-INF/container.xml', container)
        archive.writestr('EPUB/package.opf', etree.tostring(package, encoding='utf-8', xml_declaration=True))
        for name, data in resources.items():
            archive.writestr('EPUB/' + name, data)
