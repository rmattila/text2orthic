from orthic_encoder import OrthicEncoder
from glyph_renderer import GlyphRenderer
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Render Orthic shorthand text as an image.")
    parser.add_argument("text", type=str, nargs="+", help="The text to render in Orthic shorthand.", default="""The preceding rules and examples will enable the student to read the
    specimen of writing given on the opposite page, of which this page is a""")
    parser.add_argument("--space-width", type=int,
                        help="Size of inter-word spacing", default=10)
    parser.add_argument("--line-height", type=int,
                        help="Height of each line", default=100)
    parser.add_argument("--line-width", type=int,
                        help="Width of the canvas", default=1300)
    parser.add_argument("--lines-per-page", type=int,
                        help="Number of lines per page", default=float("inf"))
    args = parser.parse_args()

    renderer = GlyphRenderer()
    text = " ".join(args.text)
    rendered_image = renderer.render_text(
        text, args.space_width, args.line_height, args.line_width, args.lines_per_page)
    rendered_image.show()


if __name__ == "__main__":
    main()
