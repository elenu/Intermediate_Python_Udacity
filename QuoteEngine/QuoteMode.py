# This module defines the QuoteMode class, which is a simple data structure 
# to hold a quote's body and author.

class QuoteMode:
    """A simple QuoteMode class to encapsulate the body and author."""

    def __init__(self, body: str, author: str):
        """Initialize a QuoteMode instance.
        Args:
            body (str): The text of the quote.
            author (str): The author of the quote.
        """
        self.body = body.strip().strip('"')
        self.author = author.strip()
        if not self.body:
            raise ValueError("Quote body cannot be empty.")
        if not self.author:
            raise ValueError("Quote author cannot be empty.")

    def __str__(self):
        """Return a string representation of the QuoteMode."""
        return f'"{self.body}" - {self.author}'
    
    def __repr__(self):
        """Return an unambiguous string representation of the QuoteMode."""
        return f'QuoteMode(body="{self.body}", author="{self.author}")'
    
    def __eq__(self, other):
        """Check if two QuoteMode instances are equal based on their body and author."""
        if not isinstance(other, QuoteMode):
            return NotImplemented
        return self.body == other.body and self.author == other.author
