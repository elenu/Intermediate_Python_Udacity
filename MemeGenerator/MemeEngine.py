# Meme Engine module using Pillow to create memes by manipulating images.

from PIL import Image, ImageDraw, ImageFont
import os
import random
import textwrap
from typing import Tuple


class MemeEngine:
    """Create memes by drawing wrapped text onto images.

    Responsibilities are split into small methods to improve testability and
    enable different placement strategies.
    """

    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def _load_image(self, img_path: str, width: int) -> Image.Image:
        try:
            img = Image.open(img_path)
        except Exception as exc:
            raise Exception(f"Error opening image: {exc}")

        # Resize while keeping aspect ratio.
        aspect_ratio = img.height / img.width
        new_height = int(width * aspect_ratio)
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = getattr(Image, "LANCZOS", Image.BICUBIC)
        return img.resize((width, new_height), resample)

    def _get_font(self, base_size: int) -> ImageFont.ImageFont:
        font_path = os.path.join(
            os.path.dirname(__file__), "fonts", "LilitaOne-Regular.ttf"
        )
        try:
            return ImageFont.truetype(font_path, base_size)
        except Exception:
            try:
                arial_path = "/Library/Fonts/Arial.ttf"
                return ImageFont.truetype(arial_path, base_size)
            except Exception:
                try:
                    return ImageFont.truetype("DejaVuSans.ttf", base_size)
                except Exception:
                    return ImageFont.load_default()

    def _wrap_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.ImageFont,
        max_width: int,
    ) -> str:
        # Estimate max characters per line and use textwrap for simplicity.
        if hasattr(font, "getsize"):
            avg_char_width = font.getsize("x")[0]
        else:
            avg_char_width = 6

        max_chars = max(10, int(max_width / avg_char_width))
        return textwrap.fill(text, width=max_chars)

    def _random_position(
        self, img: Image.Image, text_size: Tuple[int, int]
    ) -> Tuple[int, int]:
        img_w, img_h = img.size
        txt_w, txt_h = text_size
        # Keep a small margin
        margin = 10
        max_x = max(margin, img_w - txt_w - margin)
        max_y = max(margin, img_h - txt_h - margin)
        return (random.randint(margin, max_x), random.randint(margin, max_y))

    def make_meme(
        self, img_path: str, text: str, author: str, width: int = 500
    ) -> str:
        # Coordinator: orchestrate the smaller steps
        img = self._load_image(img_path, width)
        draw = ImageDraw.Draw(img)
        base_font_size = max(12, int(img.height / 15))
        font = self._get_font(base_font_size)

        wrapped = self._wrap_text(draw, text, font, img.width - 20)
        author_line = f"- {author}" if author else ""

        txt_w, txt_h = self._measure_text(draw, wrapped, author_line, font)

        x, y = self._random_position(img, (txt_w, txt_h))

        self._draw_text(draw, wrapped, author_line, (x, y), font, txt_h)

        save_img, out_ext = self._prepare_save(img, img_path)
        out_path = self._save_image(save_img, out_ext)
        return out_path

    def _measure_text(
        self,
        draw: ImageDraw.ImageDraw,
        wrapped: str,
        author_line: str,
        font: ImageFont.ImageFont,
    ) -> Tuple[int, int]:
        """Return (width, height) for the wrapped text and author."""
        try:
            text_bbox = draw.multiline_textbbox((0, 0), wrapped, font=font)
            author_bbox = draw.textbbox((0, 0), author_line, font=font)
            txt_w = max(text_bbox[2], author_bbox[2])
            text_h = text_bbox[3] - text_bbox[1]
            author_h = author_bbox[3] - author_bbox[1]
            txt_h = text_h + author_h
            return txt_w, txt_h
        except Exception:
            lines = wrapped.split("\n")
            txt_w = max((font.getsize(line)[0] for line in lines), default=0)
            txt_h = sum((font.getsize(line)[1] for line in lines))
            return txt_w, txt_h

    def _draw_text(self, draw: ImageDraw.ImageDraw, wrapped: str,
                   author_line: str, position: Tuple[int, int],
                   font: ImageFont.ImageFont, txt_h: int) -> None:
        """Draw wrapped text and optional author at `position`."""
        x, y = position
        draw.multiline_text((x, y), wrapped, font=font, fill="white")
        if author_line:
            author_y = y + int(txt_h * 0.9)
            draw.text((x, author_y), author_line, font=font, fill="white")

    def _prepare_save(
        self,
        img: Image.Image,
        img_path: str,
    ) -> Tuple[Image.Image, str]:
        """Return (image_to_save, out_ext) handling transparency and ext."""
        _, in_ext = os.path.splitext(img_path)
        in_ext = in_ext.lower()
        out_ext = in_ext if in_ext in [".jpg", ".jpeg", ".png"] else ".jpg"

        save_img = img
        if out_ext in [".jpg", ".jpeg"] and img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            save_img = background
        return save_img, out_ext

    def _save_image(self, save_img: Image.Image, out_ext: str) -> str:
        """Save `save_img` to the output dir and return the path."""
        name = "meme_{}{}".format(random.randint(0, 1000000), out_ext)
        out_path = os.path.join(self.output_dir, name)
        save_format = "PNG" if out_ext == ".png" else "JPEG"
        save_img.save(out_path, format=save_format)
        return out_path
