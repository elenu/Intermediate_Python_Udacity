import os
import random

# @TODO Import your Ingestor and MemeEngine classes
from QuoteEngine.IngestorInterface import DocxIngestor, PDFIngestor, CSVIngestor, TextIngestor, IngestorInterface
from MemeGenerator.MemeEngine import MemeEngine
from QuoteEngine.QuoteMode import QuoteMode

def generate_meme(path=None, body=None, author=None):
    """ Generate a meme given an path and a quote """
    img = None
    quote = None

    if path is None:
        images = "./_data/photos/dog/"
        imgs = []
        for root, dirs, files in os.walk(images):
            imgs = [os.path.join(root, name) for name in files]
            imgs = [img for img in imgs if img.endswith('.jpg')]
        if len(imgs) == 0:
            raise Exception('No images found in directory: {}'.format(images))
        img = random.choice(imgs)
    else:
        img = path[0]

    if body is None:
        quote_files = ['./_data/DogQuotes/DogQuotesTXT.txt',
                       './_data/DogQuotes/DogQuotesDOCX.docx',
                       './_data/DogQuotes/DogQuotesPDF.pdf',
                       './_data/DogQuotes/DogQuotesCSV.csv']
        quotes = []
        for f in quote_files:
            if IngestorInterface.can_ingest(f):
                quotes.extend(DocxIngestor.parse(f))
                quotes.extend(PDFIngestor.parse(f))
                quotes.extend(CSVIngestor.parse(f))
                quotes.extend(TextIngestor.parse(f))
        if len(quotes) == 0:
            raise Exception('No quotes found in files: {}'.format(quote_files))
        quote = random.choice(quotes)
    else:
        if author is None:
            raise Exception('Author Required if Body is Used')
        quote = QuoteMode(body, author)

    meme = MemeEngine('./tmp')
    path = meme.make_meme(img, quote.body, quote.author)
    return path

if __name__ == "__main__":
    # @TODO Use ArgumentParser to parse the following CLI arguments
    # path - path to an image file
    # body - quote body to add to the image
    # author - quote author to add to the image
    args = None
    path = None
    body = None
    author = None
    import argparse
    parser = argparse.ArgumentParser(description="Generate a meme from an image and a quote.")
    parser.add_argument('--path', type=str, help='Path to an image file')
    parser.add_argument('--body', type=str, help='Quote body to add to the image')
    parser.add_argument('--author', type=str, help='Quote author to add to the image')
    args = parser.parse_args()  

    print(generate_meme(args.path, args.body, args.author))
