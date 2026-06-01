import typing
import os
from .IngestorInterface import IngestorInterface
from .QuoteMode import QuoteMode


class PDFIngestor(IngestorInterface):
    """A PDF ingestor that converts PDF to text and extracts quotes."""
    allowed_exts = ["pdf"]

    @classmethod
    def parse_pdf(cls, path: str) -> typing.List[QuoteMode]:
        import subprocess
        import tempfile

        quotes: typing.List[QuoteMode] = []
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = temp.name
        try:
            subprocess.run(
                ["pdftotext", path, temp_path], check=True
            )
            with open(temp_path, "r", encoding="utf-8") as f:
                for line in f:
                    parsed = cls._parse_line(line)
                    if not parsed:
                        continue
                    body_text, author_text = parsed
                    quotes.append(QuoteMode(body_text, author_text))
        except subprocess.CalledProcessError as e:
            raise Exception("Error converting PDF to text: {}".format(e))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        return quotes

    @classmethod
    def parse(cls, path: str) -> typing.List[QuoteMode]:
        if not cls.can_ingest(path):
            raise Exception(f"Ingestor cannot handle file: {path}")
        return cls.parse_pdf(path)
