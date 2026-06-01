# All ingestors are packaged into this main Ingestor class.
# This class encapsulates all the ingestors to provide one interface
# to load any supported file type.

import typing
from .QuoteMode import QuoteMode
from .TextIngestor import TextIngestor
from .CSVIngestor import CSVIngestor
from .DocxIngestor import DocxIngestor
from .PDFIngestor import PDFIngestor


class Ingestor:
    """Facade class that delegates parsing to concrete ingestors.

    Use `Ingestor.parse(path)` to parse any supported file type. The
    class selects an appropriate concrete ingestor based on file
    extension and returns a list of `QuoteMode` objects.
    """

    def __init__(self) -> None:
        self.allowed_exts = ["txt", "docx", "pdf", "csv"]

    # order matters if multiple ingestors claim the same extension
    ingestors = [TextIngestor, CSVIngestor, DocxIngestor, PDFIngestor]

    @classmethod
    def can_ingest(cls, path: str) -> bool:
        return any(ingestor.can_ingest(path) for ingestor in cls.ingestors)

    @classmethod
    def parse(cls, path: str) -> typing.List[QuoteMode]:
        for ingestor in cls.ingestors:
            if ingestor.can_ingest(path):
                return ingestor.parse(path)

        raise Exception(f"No ingestor found for file: {path}")
