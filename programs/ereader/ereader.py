# programs/ereader/ereader.py
import urllib.request
from fasthtml.common import *

class EReaderProgram:
    def __init__(self):
        pass  # Book loading handled by API endpoint
    
    def get_window_content(self, session=None):
        return Div(
            Div(
                H3("📖 Frankenstein"),
                P("by Mary Wollstonecraft Shelley", style="font-style: italic; color: var(--primary-dim);"),
                cls="ereader-header"
            ),
            
            Div(
                P("Loading book...", style="text-align: center; color: var(--primary-dim);"),
                cls="ereader-page", 
                id="book-content"
            ),
            
            Div(
                Button("← Previous", id="prev-btn", disabled=True),
                Span("Page 1 of 1", id="page-info"),
                Button("Next →", id="next-btn", disabled=True),
                cls="ereader-nav"
            ),
            cls="ereader-content"
        )