from orthic_encoder import OrthicEncoder
from glyph_renderer import GlyphRenderer


def main():
    word = "pRoofoprop"

    encoder = OrthicEncoder()
    renderer = GlyphRenderer()

    glyphs = encoder.encode_word(word)
    for glyph in glyphs:
        print(glyph)

    rendered_image = renderer.render_word(glyphs)

    rendered_image.show()


if __name__ == "__main__":
    main()
