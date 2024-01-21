from orthic_encoder import OrthicEncoder
from glyph_renderer import GlyphRenderer


def main():
    text = """The preceding rules and examples will enable the student to read the
    specimen of writing given on the opposite page, of which this page is a"""

    renderer = GlyphRenderer()
    rendered_image = renderer.render_text(text)
    rendered_image.show()


if __name__ == "__main__":
    main()
