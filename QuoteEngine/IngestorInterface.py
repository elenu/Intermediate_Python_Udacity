# Small abstract base class for ingestors.

import os
import typing
import abc

from .QuoteMode import QuoteMode


class IngestorInterface(abc.ABC):
    """Abstract base class for file ingestors.

    Concrete ingestors should set `allowed_exts` and implement `parse`.
    """

    allowed_exts: typing.List[str] = []

    @classmethod
    def can_ingest(cls, path: str) -> bool:
        if not os.path.isfile(path):
            return False
        ext = os.path.splitext(path)[1][1:]
        return ext in cls.allowed_exts

    @classmethod
    def _parse_line(cls, line: str):
        """Parse a single line of text into (body, author).

        Returns a tuple (body, author) or None if the line is not a quote.
        This shared helper centralizes the common 'body - author' parsing
        used by multiple ingestors.
        """
        if not line:
            return None
        line = line.strip()
        if not line:
            return None
        if " - " in line:
            body, author = line.split(" - ", 1)
        elif "," in line:
            body, author = line.rsplit(",", 1)
        else:
            return None
        return body.strip().strip('"'), author.strip()

    @classmethod
    @abc.abstractmethod
    def parse(cls, path: str) -> typing.List[QuoteMode]:
        """Parse `path` and return a list of QuoteMode objects."""
        if not cls.can_ingest(path):
            raise Exception(f"Ingestor cannot handle file: {path}")
        if path.endswith(".txt"):
            return cls.parse_txt(path)
        elif path.endswith(".docx"):
            return cls.parse_docx(path)
        elif path.endswith(".pdf"):
            return cls.parse_pdf(path)
        elif path.endswith(".csv"):
            return cls.parse_csv(path)
        else:
            raise Exception(f"Unsupported file type: {path}")
