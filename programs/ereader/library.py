# programs/ereader/library.py
from fasthtml.common import *

# Book registry - clean data structure
BOOK_REGISTRY = {
    'frankenstein': {
        'title': 'Frankenstein',
        'subtitle': 'or, The Modern Prometheus',
        'author': 'Mary Wollstonecraft Shelley',
        'year': 1818,
        'status': 'available',
    },
    'pride_prejudice': {
        'title': 'Pride and Prejudice',
        'subtitle': '',
        'author': 'Jane Austen',
        'year': 1813,
        'status': 'coming_soon',
    },
}


def LibraryView(session=None):
    """
    Main library interface - clean component responsibility
    No debug code mixed in - pure presentation logic
    """
    available_books = [
        book for book in BOOK_REGISTRY.values() if book['status'] == 'available'
    ]
    return Div(
        LibraryHeader(len(available_books)),
        BookGrid(available_books),
        LibraryActions(),
        cls='library-container',
    )


def LibraryHeader(book_count):
    """Library header component"""
    return Div(
        H2('Digital Library', cls='library-title'),
        Div(f'{book_count} books available', cls='library-stats'),
        cls='library-header',
    )


def BookGrid(books):
    """Book grid layout component"""
    return Div(
        *[
            BookCard(book_id, book_data)
            for book_id, book_data in BOOK_REGISTRY.items()
            if book_data['status'] == 'available'
        ],
        cls='book-grid',
    )


def BookCard(book_id, book_data):
    """Individual book card component"""
    return Div(
        BookCover(book_id),
        BookInfo(book_data, book_id),
        BookActions(book_id, book_data),
        cls='book-card',
        **{'data-book-id': book_id},
    )


def BookCover(book_id):
    """Book cover with SVG icon"""
    return Div(
        NotStr('<img src="/static/icons/book-open.svg" alt="Book" class="book-icon">'),
        cls='book-cover',
    )


def BookInfo(book_data, book_id):
    """Book information display"""
    subtitle_text = f': {book_data["subtitle"]}' if book_data['subtitle'] else ''

    return Div(
        H3(f'{book_data["title"]}{subtitle_text}', cls='book-title'),
        P(f'by {book_data["author"]} ({book_data["year"]})', cls='book-author'),
        BookProgress(book_data),
        cls='book-info',
    )


def make_book_id(title: str, prefix: str = '') -> str:
    """Generate consistent book IDs."""
    base_id = title.lower().replace(' ', '_')
    return f'{prefix}-{base_id}' if prefix else base_id


def LibraryWindow():
    """Library component with multiple books - pure presentation."""
    available_books = [
        book for book in BOOK_REGISTRY.values() if book['status'] == 'available'
    ]

    return Div(
        H3('📚 eReader Library', cls='library-title'),
        Div(*[BookCard(book) for book in available_books], cls='library-grid'),
        cls='library-container',
    )


def BookProgress(book_data):
    """Progress display component - client-side populated"""
    return Div(
        Div(
            'Progress loading...',
            cls='progress-label',
            id=make_book_id(book_data['title'], 'progress'),
        ),
        Div(
            Div(
                cls='progress-fill', id=make_book_id(book_data['title'], 'progress-bar')
            ),
            cls='progress-bar',
        ),
        cls='book-progress',
    )


def BookActions(book_id, book_data):
    """Book action buttons"""
    return Div(
        Button(
            'Start Reading',
            hx_post='/ereader/open',
            hx_vals=f'{{"book_id": "{book_id}"}}',
            hx_target='closest .window-content',
            cls='action-btn',
            id=f'action-{book_id}',
        ),
        cls='book-actions',
    )


def LibraryActions():
    """Library-level actions"""
    return Div(
        Button('Refresh Library', onclick='location.reload()', cls='secondary-btn'),
        cls='library-actions',
    )
