"""Artifact checks; JSON reports are evidence, not a print-house certification."""
import json
import posixpath
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
import pymupdf as fitz
from lxml import etree
from PIL import Image, ImageDraw

def check_epub(path):
    errors = []
    with zipfile.ZipFile(path) as z:
        if z.infolist()[0].filename != 'mimetype' or z.infolist()[0].compress_type != zipfile.ZIP_STORED or z.read('mimetype') != b'application/epub+zip':
            errors.append('Invalid EPUB mimetype')
        names = set(z.namelist())
        docs = {name: etree.fromstring(z.read(name)) for name in names if name.endswith(('.xhtml', '.opf', '.xml', '.svg'))}
        opf = docs['EPUB/package.opf']
        manifest = opf.findall('.//{http://www.idpf.org/2007/opf}item')
        ids = {item.get('id') for item in manifest}
        if not any('nav' in item.get('properties', '').split() for item in manifest):
            errors.append('Missing navigation')
        for item in manifest:
            if 'EPUB/' + item.get('href') not in names:
                errors.append('Missing manifest asset: ' + item.get('href'))
        for item in opf.findall('.//{http://www.idpf.org/2007/opf}itemref'):
            if item.get('idref') not in ids:
                errors.append('Invalid spine reference')
        for name, doc in docs.items():
            element_ids = doc.xpath('//@id')
            if len(element_ids) != len(set(element_ids)):
                errors.append('Duplicate IDs: ' + name)
            for el in doc.xpath('//*[@href or @src]'):
                ref = unquote(el.get('href') or el.get('src'))
                parts = urlsplit(ref)
                if parts.scheme or parts.netloc:
                    continue
                target = posixpath.normpath(posixpath.join(posixpath.dirname(name), parts.path)) if parts.path else name
                if target not in names:
                    errors.append(f'Broken resource: {name}: {ref}')
                elif parts.fragment and target in docs and parts.fragment not in docs[target].xpath('//@id'):
                    errors.append(f'Broken anchor: {name}: {ref}')
        return dict(file=path.name, kind='epub', chapters=len(opf.findall('.//{http://www.idpf.org/2007/opf}itemref')) - 3, errors=errors, warnings=[], check='Internal structure, XML, resources, anchors; run EPUBCheck for formal conformance')

def check_pdf(path, expected_size=None):
    errors, warnings, pages = [], [], []
    with fitz.open(path) as doc:
        for number, page in enumerate(doc, 1):
            rect = page.rect
            if expected_size and any(abs(a-b*72/25.4) > 1 for a,b in zip((rect.width, rect.height), expected_size)):
                errors.append(f'Page {number}: incorrect page size')
            text = page.get_text()
            if not text.strip():
                warnings.append(f'Page {number}: no extractable text')
            if '\ufffd' in text or '\x00' in text:
                errors.append(f'Page {number}: replacement / missing glyph')
            for block in page.get_text('dict')['blocks']:
                if block['type'] != 0:
                    continue
                for line in block['lines']:
                    for span in line['spans']:
                        box = fitz.Rect(span['bbox'])
                        if not (rect + (-1, -1, 1, 1)).contains(box):
                            errors.append(f'Page {number}: text outside page: {span["text"][:32]}')
            for font in page.get_fonts():
                if font[1] == 'n/a':
                    warnings.append(f'Page {number}: unembedded font {font[3]}')
            for img in page.get_image_info():
                width = img['bbox'][2] - img['bbox'][0]
                height = img['bbox'][3] - img['bbox'][1]
                dpi = min(img['width'] / max(width, 1) * 72, img['height'] / max(height, 1) * 72)
                if dpi < 250:
                    warnings.append(f'Page {number}: image resolution {dpi:.0f} DPI (<250)')
            pages.append({'page': number, 'characters': len(text.strip()), 'width_mm': round(rect.width*25.4/72, 1), 'height_mm': round(rect.height*25.4/72, 1)})
        if not doc.get_toc():
            errors.append('Missing PDF bookmarks')
        return dict(file=path.name, kind='pdf', page_count=len(doc), errors=sorted(set(errors)), warnings=sorted(set(warnings)), pages=pages)

def contact_sheet(path, destination):
    with fitz.open(path) as doc:
        thumbs = []
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(.6, .6), alpha=False)
            im = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            im.thumbnail((225, 290))
            thumbs.append(im)
        cols = 4
        cell_w = 249
        cell_h = max(im.height for im in thumbs) + 42
        sheet = Image.new('RGB', (cols*cell_w, ((len(thumbs)+cols-1)//cols)*cell_h), '#e5e2da')
        draw = ImageDraw.Draw(sheet)
        for i, im in enumerate(thumbs):
            x = (i%cols)*cell_w + (cell_w-im.width)//2
            y = (i//cols)*cell_h + 10
            sheet.paste(im, (x,y))
            draw.text(((i%cols)*cell_w+12, (i//cols)*cell_h+cell_h-20), f'{i+1:02d}', fill='#202a29')
        sheet.save(destination)
