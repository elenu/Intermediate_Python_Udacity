import typing
from .IngestorInterface import IngestorInterface
from .QuoteMode import QuoteMode


class DocxIngestor(IngestorInterface):
    """Docx ingestor that parses docx files into QuoteMode objects."""
    allowed_exts = ["docx"]

    @classmethod
    def parse_docx(cls, path: str) -> typing.List[QuoteMode]:
        try:
            from docx import Document
        except Exception as e:
            raise Exception(
                "python-docx is required to parse docx files: {}".format(e)
            )

        quotes: typing.List[QuoteMode] = []
        doc = Document(path)
        for para in doc.paragraphs:
            parsed = cls._parse_line(para.text)
            if not parsed:
                continue
            body_text, author_text = parsed
            quotes.append(QuoteMode(body_text, author_text))
        return quotes

    @classmethod
    def parse(cls, path: str) -> typing.List[QuoteMode]:
        if not cls.can_ingest(path):
            raise Exception(f"Ingestor cannot handle file: {path}")
        return cls.parse_docx(path)
