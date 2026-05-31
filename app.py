import random
import os
import requests
import flask

# @TODO Import your Ingestor and MemeEngine classes
from QuoteEngine.Ingestor import Ingestor
from MemeGenerator.MemeEngine import MemeEngine
from QuoteEngine import QuoteMode

app = flask.Flask(__name__)

# Use paths relative to this file so the app can be run from any CWD
base_dir = os.path.dirname(__file__)
meme = MemeEngine(os.path.join(base_dir, 'static'))

def setup():
    """ Load all resources """

    quote_files = [
        os.path.join(base_dir, '_data', 'DogQuotes', 'DogQuotesTXT.txt'),
        os.path.join(base_dir, '_data', 'DogQuotes', 'DogQuotesDOCX.docx'),
        os.path.join(base_dir, '_data', 'DogQuotes', 'DogQuotesPDF.pdf'),
        os.path.join(base_dir, '_data', 'DogQuotes', 'DogQuotesCSV.csv'),
    ]

    # TODO: Use the Ingestor class to parse all files in the
    # quote_files variable
    quotes = None

    images_path = os.path.join(base_dir, '_data', 'photos', 'dog')

    if not Ingestor.can_ingest(quote_files[0]):
        raise Exception('Cannot ingest file: {}'.format(quote_files[0]))
    quotes = Ingestor.parse(quote_files[0])
    quotes += Ingestor.parse(quote_files[1])
    quotes += Ingestor.parse(quote_files[2])
    quotes += Ingestor.parse(quote_files[3])

    # TODO: Use the pythons standard library os class to find all
    # images within the images images_path directory
    imgs = None
    os.walk(images_path)
    imgs = [os.path.join(images_path, img) for img in os.listdir(images_path)]
    imgs = [img for img in imgs if img.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if len(imgs) == 0:
        raise Exception('No images found in directory: {}'.format(images_path))

    return quotes, imgs

quotes, imgs = setup()

@app.route('/')
def meme_rand():
    """ Generate a random meme """

    # @TODO:
    # Use the random python standard library class to:
    # 1. select a random image from imgs array
    # 2. select a random quote from the quotes array

    img = None
    quote = None
    img = random.choice(imgs)
    quote = random.choice(quotes)

    path = meme.make_meme(img, quote.body, quote.author)
    # Convert filesystem path to a URL relative to the `static` folder
    filename = os.path.basename(path)
    url = flask.url_for('static', filename=filename)
    return flask.render_template('meme.html', path=url)

@app.route('/create', methods=['GET'])
def meme_form():
    """ User input for meme information """
    return flask.render_template('meme_form.html')

@app.route('/create', methods=['POST'])
def meme_post():
    """ Create a user defined meme """

    # @TODO:
    # 1. Use requests to save the image from the image_url
    #    form param to a temp local file.
    # 2. Use the meme object to generate a meme using this temp
    #    file and the body and author form paramaters.
    # 3. Remove the temporary saved image.

    path = None
    request_url = flask.request.form.get('image_url')

    if not request_url:
        flask.abort(400, description='`image_url` is required')

    try:
        response = requests.get(request_url, timeout=10)
    except requests.RequestException as e:
        flask.abort(400, description=f'Error fetching image URL: {e}')

    if response.status_code != 200:
        flask.abort(400, description='Invalid image URL: {}'.format(request_url))

    temp_image_path = './temp_image.jpg'
    try:
        with open(temp_image_path, 'wb') as f:
            f.write(response.content)

        body = flask.request.form.get('body')
        author = flask.request.form.get('author')

        try:
            path = meme.make_meme(temp_image_path, body, author)
        except Exception as e:
            flask.abort(500, description=f'Error creating meme: {e}')
    finally:
        if os.path.exists(temp_image_path):
            try:
                os.remove(temp_image_path)
            except Exception:
                pass
    # Convert filesystem path to a URL relative to the `static` folder
    filename = os.path.basename(path)
    url = flask.url_for('static', filename=filename)
    return flask.render_template('meme.html', path=url)

if __name__ == "__main__":
    app.run()
