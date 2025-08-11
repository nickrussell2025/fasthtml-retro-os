# programs/ereader/library.py
from fasthtml.common import *

# Book registry - clean data structure
BOOK_REGISTRY = {
    "frankenstein": {
        "title": "Frankenstein",
        "subtitle": "or, The Modern Prometheus", 
        "author": "Mary Wollstonecraft Shelley",
        "year": 1818,
        "status": "available"
    },
    "pride_prejudice": {
        "title": "Pride and Prejudice",
        "subtitle": "",
        "author": "Jane Austen", 
        "year": 1813,
        "status": "coming_soon"
    }
}

def LibraryView(session=None):
    """
    Main library interface - clean component responsibility
    No debug code mixed in - pure presentation logic
    """
    available_books = [book for book in BOOK_REGISTRY.values() if book["status"] == "available"]
    
    return Div(
        LibraryHeader(len(available_books)),
        BookGrid(available_books),
        LibraryActions(),
        cls="library-container"
    )

def LibraryHeader(book_count):
    """Library header component"""
    return Div(
        H2("Digital Library", cls="library-title"),
        Div(f"{book_count} books available", cls="library-stats"),
        cls="library-header"
    )

def BookGrid(books):
    """Book grid layout component"""
    return Div(
        *[BookCard(book_id, book_data) for book_id, book_data in BOOK_REGISTRY.items() 
          if book_data["status"] == "available"],
        cls="book-grid"
    )

def BookCard(book_id, book_data):
    """Individual book card component"""
    return Div(
        BookCover(book_id),
        BookInfo(book_data, book_id),
        BookActions(book_id, book_data),
        cls="book-card",
        **{"data-book-id": book_id}
    )

def BookCover(book_id):
    """Book cover with SVG icon"""
    return Div(
        NotStr('<img src="/static/icons/book-open.svg" alt="Book" class="book-icon">'),
        cls="book-cover"
    )

def BookInfo(book_data, book_id):
    """Book information display"""
    subtitle_text = f": {book_data['subtitle']}" if book_data["subtitle"] else ""
    
    return Div(
        H3(f"{book_data['title']}{subtitle_text}", cls="book-title"),
        P(f"by {book_data['author']} ({book_data['year']})", cls="book-author"),
        BookProgress(book_data, book_id),
        cls="book-info"
    )

def BookProgress(book_data, book_id):
    """Progress display component - client-side populated"""
    return Div(
        Div("Progress loading...", cls="progress-label", id=f"progress-{book_data['title'].lower().replace(' ', '_')}"),
        Div(
            Div(cls="progress-fill", id=f"progress-bar-{book_data['title'].lower().replace(' ', '_')}"),
            cls="progress-bar"
        ),
        cls="progress-section"
    )

def BookActions(book_id, book_data):
    """Book action buttons"""
    return Div(
        Button(
            "Start Reading",
            hx_post="/ereader/open",
            hx_vals=f'{{"book_id": "{book_id}"}}',
            hx_target="closest .window-content",
            cls="action-btn",
            id=f"action-{book_id}"
        ),
        cls="book-actions"
    )

def LibraryActions():
    """Library-level actions"""
    return Div(
        Button("Refresh Library", onclick="location.reload()", cls="secondary-btn"),
        cls="library-actions"
    )