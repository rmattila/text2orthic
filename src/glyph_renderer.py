from PIL import Image


def sign(x: int):
    return (x > 0) - (x < 0)


class GlyphRenderer:
    def __init__(self, glyph_folder="../resources/glyphs"):
        self.glyph_folder = glyph_folder

    def render_word(self, glyphs):
        # Start with an empty canvas
        canvas = Image.new("RGBA", (1, 1), (255, 255, 255, 0))
        last_position = (64, 64)  # Starting position

        for glyph in glyphs:
            img = self.load_glyph_image(glyph.symbol)
            start_pos, end_pos = self.find_glyph_start_end_positions(img)

            # Hide alignment pixels
            img = self.replace_alignment_pixels(img)

            if not start_pos:
                print(f"Could not find start position (green pixel) in {glyph.symbol}")
                continue

            if not end_pos:
                print(f"Could not find end position (red pixel) in {glyph.symbol}")
                continue

            if glyph.symbol != "Unknown":
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
        canvas = self.paste_on_white_background(canvas)

        return canvas

    def load_glyph_image(self, symbol):
        # Load the glyph image
        img = Image.open(f"{self.glyph_folder}/{symbol}.png")

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

        # Check if canvas needs to be resized
        new_width = max(canvas.width, x_offset + glyph_img.width)
        new_height = max(canvas.height, y_offset + glyph_img.height)

        # Resize canvas if needed
        if new_width > canvas.width or new_height > canvas.height:
            new_canvas = Image.new("RGBA", (new_width, new_height), (255, 255, 255, 0))
            new_canvas.alpha_composite(canvas)
            canvas = new_canvas

        # Paste the glyph onto the canvas
        canvas.alpha_composite(glyph_img, (x_offset, y_offset))
        return canvas

    def replace_alignment_pixels(self, canvas):
        for y in range(canvas.height):
            for x in range(canvas.width):
                pixel = canvas.getpixel((x, y))
                if pixel[0:3] == (0, 255, 0) or pixel[0:3] == (
                    255,
                    0,
                    0,
                ):  # Green or Red
                    canvas.putpixel((x, y), (0, 0, 0))  # Replace with black

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
