# This module defines the Ingestor class, which can parse various file formats 
# (txt, csv, docx, pdf) to extract quotes and authors, returning a list of 
# QuoteModel objects. 
# It uses the python-docx library for docx files and PyPDF2 for pdf files.

import os
import typing
import abc
from .QuoteMode import QuoteMode

class IngestorInterface(abc.ABC):
    """Abstract base class for file ingestors.

    Concrete ingestors (TextIngestor, CSVIngestor, DocxIngestor, PDFIngestor)
    should implement the corresponding `parse_*` classmethods.
    """
    # class-level allowed extensions so classmethods can access it
    allowed_exts = ['txt', 'docx', 'pdf', 'csv']
    def __init__(self) -> None:
        self.allowed_exts = ['txt', 'docx', 'pdf', 'csv']
        
    @classmethod
    def can_ingest(cls, path: str) -> bool:
        if not os.path.isfile(path):
            return False
        ext = os.path.splitext(path)[1][1:]
        return ext in cls.allowed_exts
    @classmethod
    @abc.abstractmethod
    def parse(cls, path: str) -> typing.List[QuoteMode]:
        """Parse the file at `path` and return a list of QuoteMode objects.

        Concrete ingestor classes must implement this method.
        """
        if not cls.can_ingest(path):
            raise Exception(f'Ingestor cannot handle file: {path}')
        if path.endswith('.txt'):
            return cls.parse_txt(path)
        if path.endswith('.csv'):
            return cls.parse_csv(path)
        if path.endswith('.docx'):
            return cls.parse_docx(path)
        if path.endswith('.pdf'):
            return cls.parse_pdf(path)
        raise Exception(f'Unsupported file type: {path}')

class TextIngestor(IngestorInterface):
    """A simple TextIngestor that can parse txt files into QuoteMode objects."""
    def __init__(self) -> None:
        self.allowed_exts = ['txt']
    allowed_exts = ['txt']
    @classmethod
    def parse_txt(cls, path: str) -> typing.List[QuoteMode]:
        quotes = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if ' - ' in line:
                    body, author = line.split(' - ', 1)
                elif ',' in line:
                    body, author = line.rsplit(',', 1)
                else:
                    continue
                quotes.append(QuoteMode(body.strip().strip('"'), author.strip()))
        return quotes
    @classmethod
    def parse(cls, path: str) -> typing.List[QuoteMode]:
        if not cls.can_ingest(path):
            raise Exception(f'Ingestor cannot handle file: {path}')
        return cls.parse_txt(path)

class DocxIngestor(IngestorInterface):
    """A simple DocxIngestor that can parse docx files into QuoteMode objects."""
    allowed_exts = ['docx']
    def __init__(self) -> None:
        self.allowed_exts = ['docx']
    @classmethod
    def parse_docx(cls, path: str) -> typing.List[QuoteMode]:
        try:
            from docx import Document
        except Exception as e:
            raise Exception('python-docx is required to parse docx files: {}'.format(e))
        quotes = []
        doc = Document(path)
        for para in doc.paragraphs:
            line = para.text.strip()
            if not line:
                continue
            if ' - ' in line:
                body, author = line.split(' - ', 1)
                quotes.append(QuoteMode(body.strip().strip('"'), author.strip()))
        return quotes
    @classmethod
    def parse(cls, path: str) -> typing.List[QuoteMode]:
        if not cls.can_ingest(path):
            raise Exception(f'Ingestor cannot handle file: {path}')
        return cls.parse_docx(path)
    
class PDFIngestor(IngestorInterface):
    """A simple PDFIngestor that can parse pdf files into QuoteMode objects."""
    allowed_exts = ['pdf']
    def __init__(self) -> None:
        self.allowed_exts = ['pdf']
    @classmethod
    def parse_pdf(cls, path: str) -> typing.List[QuoteMode]:
        import subprocess
        import tempfile
        quotes = []
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = temp.name
        try:
            subprocess.run(['pdftotext', path, temp_path], check=True)
            with open(temp_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if ' - ' in line:
                        body, author = line.split(' - ', 1)
                        quotes.append(QuoteMode(body.strip().strip('"'), author.strip()))
        except subprocess.CalledProcessError as e:
            raise Exception('Error converting PDF to text: {}'.format(e))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        return quotes
    @classmethod
    def parse(cls, path: str) -> typing.List[QuoteMode]:
        if not cls.can_ingest(path):
            raise Exception(f'Ingestor cannot handle file: {path}')
        return cls.parse_pdf(path)

class CSVIngestor(IngestorInterface):
    """A simple CSVIngestor that can parse csv files into QuoteMode objects."""
    allowed_exts = ['csv']
    def __init__(self) -> None:
        self.allowed_exts = ['csv']
    @classmethod
    def parse_csv(cls, path: str) -> typing.List[QuoteMode]:
        import csv
        quotes = []
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                body = row.get('body') or row.get('quote') or list(row.values())[0]
                author = row.get('author') or (list(row.values())[1] if len(row.values()) > 1 else '')
                quotes.append(QuoteMode(body.strip().strip('"'), author.strip()))
        return quotes
    @classmethod
    def parse(cls, path: str) -> typing.List[QuoteMode]:
        if not cls.can_ingest(path):
            raise Exception(f'Ingestor cannot handle file: {path}')
        return cls.parse_csv(path)

