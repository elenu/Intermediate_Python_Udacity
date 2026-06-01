import typing
from .IngestorInterface import IngestorInterface
from .QuoteMode import QuoteMode


class TextIngestor(IngestorInterface):
    """Text ingestor for parsing txt files into QuoteMode objects."""
    allowed_exts = ["txt"]

    @classmethod
    def parse_txt(cls, path: str) -> typing.List[QuoteMode]:
        quotes: typing.List[QuoteMode] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                parsed = cls._parse_line(line)
                if not parsed:
                    continue
                body_text, author_text = parsed
                quotes.append(QuoteMode(body_text, author_text))
        return quotes

    @classmethod
    def parse(cls, path: str) -> typing.List[QuoteMode]:
        if not cls.can_ingest(path):
            raise Exception(f"Ingestor cannot handle file: {path}")
        return cls.parse_txt(path)
