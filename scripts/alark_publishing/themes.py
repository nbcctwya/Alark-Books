"""Theme resources shared by PDF/HTML and EPUB exporters."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Theme:
    template: str
    styles: tuple[str, ...] = ()
    epub_style: str | None = None
    landscape_columns: bool = True

THEMES = {
    'folio': Theme('folio.html.j2', ('folio.css', 'folio-screen.css'), 'folio-epub.css', False),
    'editorial': Theme('book.html.j2', ('editorial.css', 'editorial-screen.css'), 'editorial-epub.css'),
    'spectacle': Theme('spectacle.html.j2', ('spectacle.css', 'spectacle-screen.css'), 'spectacle-epub.css', False),
    'business': Theme('studio.html.j2', ('business.css', 'business-screen.css'), 'business-epub.css'),
    'investment': Theme('studio.html.j2', ('investment.css', 'investment-screen.css'), 'investment-epub.css'),
}
