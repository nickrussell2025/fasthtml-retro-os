# programs/ereader/ereader.py
from fasthtml.common import *


class EReaderProgram:
    def __init__(self):
        self.mode = 'library'  # Default to library mode

    def get_window_content(self, session=None, book_id=None):
        """
        Main entry point - decides between library and book view
        Clean separation of concerns
        """
        if book_id:
            self.mode = 'reader'
            return self._get_book_reader_content(book_id, session)
        else:
            self.mode = 'library'
            return self._get_library_content(session)

    def _get_library_content(self, session):
        """Return library interface"""
        from .library import LibraryView

        return LibraryView(session)

    def _get_book_reader_content(self, book_id, session):
        """Return book reader interface for specific book"""
        from .library import BOOK_REGISTRY

        book = BOOK_REGISTRY[book_id]

        return Div(
            Div(
                Button(
                    '🏠',
                    hx_get='/ereader/library',
                    hx_target='closest .window-content',
                    cls='home-btn',
                ),
                H3(f'📖 {book["title"]}'),
                P(
                    f'by {book["author"]}',
                    style='font-style: italic; color: var(--primary-dim);',
                ),
                cls='ereader-header',
            ),
            # Progress bars from Feature 1
            Div(
                Div(id='chapter-progress-fill', cls='chapter-progress-fill'),
                cls='chapter-progress-container',
            ),
            Div(
                Div(id='book-progress-fill', cls='book-progress-fill'),
                cls='book-progress-container',
            ),
            Div(
                P(
                    'Loading book content...',
                    style='text-align: center; color: var(--primary-dim);',
                ),
                cls='ereader-page',
                id='book-content',
                **{'data-book-id': book_id},
            ),
            Div(
                Button('← Previous', id='prev-btn', disabled=True),
                Span('Page 1 of 1', id='page-info'),
                Button('Next →', id='next-btn', disabled=True),
                cls='ereader-nav',
            ),
            cls='ereader-content',
        )
