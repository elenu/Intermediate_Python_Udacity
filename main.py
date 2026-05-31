#!/usr/bin/env python3
"""Simple runner to generate a random captioned image.

This script uses the QuoteEngine.Ingestor facade to parse quote files
(txt/csv/docx/pdf) and the MemeGenerator.MemeEngine to compose an image.

Usage:
    python main.py

It will print the path to the generated meme image.
"""
import os
import random
import sys
import argparse

from QuoteEngine.Ingestor import Ingestor
import MemeGenerator.MemeEngine

base_dir = os.path.dirname(__file__)

data_quotes = os.path.join(base_dir, '_data', 'DogQuotes')
data_images = os.path.join(base_dir, '_data', 'photos', 'dog')
output_dir = os.path.join(base_dir, 'static')


def load_quotes():
    quotes = []
    # collect supported files from the quotes directory
    for fname in os.listdir(data_quotes):
        path = os.path.join(data_quotes, fname)
        if not os.path.isfile(path):
            continue
        try:
            if Ingestor.can_ingest(path):
                quotes += Ingestor.parse(path)
        except Exception as e:
            print(f'Warning: failed to parse {path}: {e}', file=sys.stderr)
    return quotes


def load_images():
    imgs = []
    if not os.path.isdir(data_images):
        return imgs
    for fname in os.listdir(data_images):
        if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
            imgs.append(os.path.join(data_images, fname))
    return imgs


def main():
    parser = argparse.ArgumentParser(description='Generate a meme from quotes and images')
    parser.add_argument('--body', type=str, help='Quote body (optional)')
    parser.add_argument('--author', type=str, help='Quote author (optional)')
    parser.add_argument('--path', type=str, help='Path to an image file (optional)')
    args = parser.parse_args()

    quotes = load_quotes()
    imgs = load_images()

    if not quotes and not args.body:
        print('No quotes found; cannot generate meme unless --body is provided.', file=sys.stderr)
        sys.exit(1)
    if not imgs and not args.path:
        print('No images found; cannot generate meme unless --path is provided.', file=sys.stderr)
        sys.exit(1)

    # choose image: provided path or random
    if args.path:
        img = args.path
        if not os.path.isfile(img):
            print(f'Image path not found: {img}', file=sys.stderr)
            sys.exit(1)
    else:
        img = random.choice(imgs)

    # choose quote: provided body (and optional author) or random
    if args.body:
        body = args.body
        author = args.author if args.author else 'Unknown'
    else:
        quote = random.choice(quotes)
        body = quote.body
        author = quote.author

    me = MemeGenerator.MemeEngine.MemeEngine(output_dir)
    out = me.make_meme(img, body, author)
    print(out)


if __name__ == '__main__':
    main()
