import typing
from .IngestorInterface import IngestorInterface
from .QuoteMode import QuoteMode


class CSVIngestor(IngestorInterface):
    """CSV ingestor using pandas to parse CSV files into QuoteMode objects.

    Uses pandas to read tabular data and converts rows to `QuoteMode`.
    """
    allowed_exts = ["csv"]

    @classmethod
    def parse_csv(cls, path: str) -> typing.List[QuoteMode]:
        try:
            import pandas as pd
        except Exception as e:
            raise Exception(
                "pandas is required to parse CSV files: {}".format(e)
            )

        df = pd.read_csv(path, dtype=str)
        quotes: typing.List[QuoteMode] = []
        for _, row in df.iterrows():
            # Try common column names, fall back to positional values
            body = None
            author = None
            if "body" in row.index:
                body = row["body"]
            elif "quote" in row.index:
                body = row["quote"]
            else:
                # use first column if available
                if len(row.index) >= 1:
                    body = row.iloc[0]

            if "author" in row.index:
                author = row["author"]
            else:
                # use second column if available
                if len(row.index) >= 2:
                    author = row.iloc[1]

            if body is None:
                continue
            if pd.isna(body):
                continue
            body_text = str(body).strip().strip('"')
            if author is None or pd.isna(author):
                author_text = ""
            else:
                author_text = str(author).strip()

            quotes.append(QuoteMode(body_text, author_text))

        return quotes

    @classmethod
    def parse(cls, path: str) -> typing.List[QuoteMode]:
        if not cls.can_ingest(path):
            raise Exception(f"Ingestor cannot handle file: {path}")
        return cls.parse_csv(path)
