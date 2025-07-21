# programs/ereader/routes.py
import urllib.request
from fasthtml.common import Div, Response
from .ereader import EReaderProgram

def setup_ereader_routes(app):
    """Setup eReader routes"""
    
    @app.post("/ereader/page/{page_num}")
    def ereader_navigate(page_num: int, session):
        """Handle eReader page navigation"""
        try:
            # Update session with new page
            session['ereader_page'] = page_num
            
            # Get updated content
            program = EReaderProgram()
            return program.get_window_content(session)
            
        except Exception as e:
            print(f"ERROR in ereader_navigate: {e}")
            return Div(f"Error: {str(e)}")
    
    @app.get("/api/book/frankenstein")
    def get_frankenstein():
        """Serve the full Frankenstein text"""
        try:
            url = "https://www.gutenberg.org/files/84/84-0.txt"
            with urllib.request.urlopen(url) as response:
                text = response.read().decode('utf-8')
            
            start_idx = text.find("CHAPTER I")
            end_idx = text.find("End of the Project Gutenberg EBook")
            
            if start_idx != -1 and end_idx != -1:
                book_text = text[start_idx:end_idx].strip()
            else:
                book_text = text
                
            return Response(content=book_text, media_type="text/plain")
            
        except Exception as e:
            return Response(content=f"Error loading book: {str(e)}", media_type="text/plain")