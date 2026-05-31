# This is the Meme Engine module, which uses the Pillow library to create 
# memes by manipulating images.

from PIL import Image, ImageDraw, ImageFont
import os
import random

class MemeEngine:
    """A class to create memes by manipulating images using Pillow (PIL)."""

    def __init__(self, output_dir):
        """Initialize the MemeEngine with the specified output directory."""
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def make_meme(self, img_path, text, author, width=500) -> str:
        """Create a meme by adding text and author to the image."""
        try:
            img = Image.open(img_path)
        except Exception as e:
            raise Exception(f"Error opening image: {e}")

        # Resize the image while maintaining aspect ratio
        aspect_ratio = img.height / img.width
        new_height = int(width * aspect_ratio)
        # Pillow 10+ moved resampling filters; provide compatibility fallback
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = getattr(Image, 'LANCZOS', Image.BICUBIC)
        img = img.resize((width, new_height), resample)

        draw = ImageDraw.Draw(img)
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'LilitaOne-Regular.ttf')
        font_size = int(new_height / 15)

        # Try to load a bundled font, fall back to a system font or PIL default
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception:
            try:
                # Common macOS font location
                font = ImageFont.truetype('/Library/Fonts/Arial.ttf', font_size)
            except Exception:
                try:
                    # DejaVu is common on many systems
                    font = ImageFont.truetype('DejaVuSans.ttf', font_size)
                except Exception:
                    font = ImageFont.load_default()

        # Add text to the image
        text_position = (10, new_height - font_size * 2 - 10)
        author_position = (10, new_height - font_size - 10)
        
        draw.text(text_position, text, font=font, fill='white')
        draw.text(author_position, f'- {author}', font=font, fill='white')

        # Preserve input extension if it's a supported image format, else default to .jpg
        _, in_ext = os.path.splitext(img_path)
        in_ext = in_ext.lower()
        if in_ext in ['.jpg', '.jpeg', '.png']:
            out_ext = in_ext
        else:
            out_ext = '.jpg'

        # If image has alpha and we're saving as JPEG, composite over white background
        save_img = img
        if out_ext in ['.jpg', '.jpeg'] and img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            save_img = background

        output_path = os.path.join(self.output_dir, f'meme_{random.randint(0,1000000)}{out_ext}')
        save_format = 'PNG' if out_ext == '.png' else 'JPEG'
        save_img.save(output_path, format=save_format)
        
        return output_path  
