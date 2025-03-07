from typing import List
from PIL import Image
from tqdm import tqdm
from importlib import resources

from glyph import Glyph, SPECIAL_SYMBOLS
from orthic_encoder import OrthicEncoder


def sign(x: int):
    return (x > 0) - (x < 0)


class GlyphRenderer:
    def __init__(self, glyph_folder=resources.files('glyphs')):
        self.glyph_folder = glyph_folder

    def render_text(
        self,
        text: str,
        space_width=10,
        line_height=100,
        line_width=1300,
        lines_per_page=float("inf"),
    ):
        """
        Renders Orthic shorthand text as an image or a series of images (pages).

        This function takes a string of English text and converts it into Orthic shorthand.
        The rendered text is then composed onto an image canvas. If `lines_per_page` is set to a finite number,
        the text is split into multiple pages, each containing the specified number of lines.
        Otherwise, the entire text is rendered onto a single image.

        Args:
            text (str): The English text to be rendered in Orthic shorthand.
            space_width (int, optional): The space between words in pixels. Defaults to 10.
            line_height (int, optional): The height of each line in pixels. Defaults to 100.
            line_width (int, optional): The width of the canvas in pixels. Defaults to 1300.
            lines_per_page (int, optional): The maximum number of lines per page. Defaults to float("inf"),
                which indicates no pagination.

        Returns:
            list or Image: A list of PIL Image objects, each representing a page, if `lines_per_page` is finite.
            If `lines_per_page` is infinite, a single Image object is returned representing the entire text.
        """
        words = text.split()
        pages = []
        current_line = 1
        canvas = Image.new("RGBA", (line_width, line_height), (255, 255, 255, 0))
        x, y = 0, line_height

        for word in tqdm(words):
            word_img = self.render_word(word, transparent_background=True)
            if x + word_img.width > line_width:
                x = 0
                y += line_height
                current_line += 1

                # paginate
                if current_line > lines_per_page:
                    # render and save
                    canvas = self.crop_to_content(canvas)
                    canvas = self.paste_on_white_background(canvas)

                    pages.append(canvas)

                    # create a fresh page
                    canvas = Image.new(
                        "RGBA", (line_width, line_height), (255, 255, 255, 0)
                    )
                    x, y = 0, line_height
                    current_line = 1

            if y + word_img.height > canvas.height:
                canvas = self.expand_canvas(canvas, line_width, y + word_img.height)

            canvas.alpha_composite(word_img, (x, y - word_img.height // 2))
            x += word_img.width + space_width

        canvas = self.crop_to_content(canvas)
        canvas = self.paste_on_white_background(canvas)

        pages.append(canvas)

        return pages if lines_per_page != float("inf") else pages[0]

    def render_word(self, word: str, transparent_background: bool = False):
        encoder = OrthicEncoder()
        glyphs = encoder.encode_word(word)

        n_unknown_glyphs = sum(glyph.symbol == "Unknown" for glyph in glyphs)
        if n_unknown_glyphs > 0:
            tqdm.write(
                f"Encountered {n_unknown_glyphs} unknown glyphs when rendering the word '{word}'"
            )

        # Start with an empty (big) canvas
        #   This is a bit wasteful; we should dynamically resize the canvas,
        #   but that turned out to be a bit messy to get correct (since we also
        #   need to pad incase, say, multiple p:s leave the canvas on the left).
        canvas = Image.new("RGBA", (100 * 45 + 512, 1024), (255, 255, 255, 0))
        last_position = (512, 512)  # Starting position

        for glyph in glyphs:
            if glyph.symbol != "Unknown":
                img = self.load_glyph_image(glyph.symbol)
                start_pos, end_pos = self.find_glyph_start_end_positions(img)

                # Hide alignment pixels
                if glyph.symbol in SPECIAL_SYMBOLS:
                    # if non-connected symbol (e.g., a number or a semicolon) put transparent pixel
                    img = self.replace_alignment_pixels(img, (0, 0, 0, 0))
                else:
                    # otherwise use black
                    img = self.replace_alignment_pixels(img)

                if not start_pos:
                    tqdm.write(
                        f"Could not find start position (green pixel) in {glyph.symbol}"
                    )
                    continue

                if not end_pos:
                    tqdm.write(
                        f"Could not find end position (red pixel) in {glyph.symbol}"
                    )
                    continue

                canvas = self.place_glyph(canvas, img, last_position, start_pos)
                last_position = (
                    last_position[0] + end_pos[0] - start_pos[0],
                    last_position[1] + end_pos[1] - start_pos[1],
                )

                if glyph.double:
                    # Indicate a double-letter with a dot below
                    dot_img = self.load_glyph_image("doubled_dot")
                    dot_pos = (
                        last_position[0]
                        - (img.width // 2) * sign(end_pos[0] - start_pos[0]),
                        last_position[1] - end_pos[1] + start_pos[1] + img.height,
                    )

                    canvas = self.place_glyph(canvas, dot_img, dot_pos, (0, 0))

        canvas = self.crop_to_content(canvas)

        # Check if there is any capital letter in the word,
        # if so, add an indicator below the word
        if any(glyph.capital for glyph in glyphs):
            indicator_img = self.load_glyph_image("capital_mark")
            old_height = canvas.height
            canvas = self.expand_canvas(
                canvas,
                max(canvas.width, indicator_img.width),
                canvas.height + indicator_img.height,
            )
            canvas.alpha_composite(indicator_img, (0, old_height))

        if not transparent_background:
            canvas = self.paste_on_white_background(canvas)

        return canvas

    def load_glyph_image(self, symbol):
        # Load the glyph image
        path = self.glyph_folder.joinpath(f"{symbol}.png")
        img = Image.open(path)

        # Parse transparency
        img = self.convert_grayscale_to_alpha(img)

        return img

    def convert_grayscale_to_alpha(self, img):
        img = img.convert("RGBA")

        for y in range(img.height):
            for x in range(img.width):
                r, g, b, _ = img.getpixel((x, y))

                # Skip red and green pixels
                if (r, g, b) == (255, 0, 0) or (r, g, b) == (0, 255, 0):
                    continue

                # Convert grayscale to alpha
                grayscale = int(0.299 * r + 0.587 * g + 0.114 * b)
                alpha = 255 - grayscale
                img.putpixel((x, y), (0, 0, 0, alpha))

        return img

    def find_glyph_start_end_positions(self, img):
        start_position = end_position = None
        for y in range(img.height):
            for x in range(img.width):
                pixel = img.getpixel((x, y))
                if pixel == (0, 255, 0, 255):  # Green pixel
                    start_position = (x, y)
                elif pixel == (255, 0, 0, 255):  # Red pixel
                    end_position = (x, y)
        return start_position, end_position

    def place_glyph(self, canvas, glyph_img, last_position, start_position):
        # Calculate the offset for placement
        x_offset = last_position[0] - start_position[0]
        y_offset = last_position[1] - start_position[1]

        # Paste the glyph onto the canvas
        canvas.alpha_composite(glyph_img, (x_offset, y_offset))
        return canvas

    def expand_canvas(self, canvas, new_width, new_height):
        new_canvas = Image.new("RGBA", (new_width, new_height), (255, 255, 255, 0))
        new_canvas.paste(canvas)
        return new_canvas

    def replace_alignment_pixels(self, canvas, color=(0, 0, 0)):
        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.getpixel((x, y))
                if pixel[0:3] == (0, 255, 0) or pixel[0:3] == (
                    255,
                    0,
                    0,
                ):  # Green or Red
                    canvas.putpixel((x, y), color)

        return canvas

    def crop_to_content(self, canvas):
        bbox = canvas.getbbox()
        return canvas.crop(bbox) if bbox else canvas

    def paste_on_white_background(self, canvas):
        # Create a white background image
        white_bg = Image.new("RGBA", canvas.size, "white")
        # Paste the canvas onto the white background
        white_bg.alpha_composite(canvas)
        return white_bg
