import PySimpleGUI as sg
from PIL import ImageOps

from orthic_encoder import OrthicEncoder
from glyph_renderer import GlyphRenderer


def create_thumbnail(image, max_size=(550, 200)):
    thumbnail = image.copy()
    thumbnail.thumbnail(max_size)
    return thumbnail


def expand_canvas(img, target_width, target_height, padding_size):
    # First, add padding around the original image
    padded_img = ImageOps.expand(img, border=padding_size, fill="white")

    # Calculate how much to expand on the right and bottom after padding
    right_padding = max(target_width - padded_img.width, 0)
    bottom_padding = max(target_height - padded_img.height, 0)

    # Apply additional padding to expand to the target size
    return ImageOps.expand(
        padded_img, border=(0, 0, right_padding, bottom_padding), fill="white"
    )


def main():
    layout = [
        [sg.Text("Enter text to transcribe:")],
        [sg.Multiline(key="-INPUT-", size=(80, 20))],
        [
            sg.Button("Transcribe"),
            sg.Button("Open in Viewer"),
            sg.Button("Export to PDF"),
            sg.Column([], expand_x=True),
            sg.Button("About"),
            sg.Button("Exit"),
        ],
        [
            sg.Column([], expand_x=True),
            sg.Image(key="-IMAGE-"),
            sg.Column([], expand_x=True),
        ],
        [
            sg.Text(
                "Image is resized. Click 'Open in Viewer' for full size.",
                key="-INFO-",
                visible=False,
            )
        ],
    ]

    window = sg.Window("text2orthic", layout)
    orthic_image = None

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        if event == "Transcribe":
            text = values["-INPUT-"]

            if text:
                # render text to orthic
                orthic_image = GlyphRenderer().render_text(text)
                img_path = (
                    "temp_output.png"  # Temporary file to save the rendered image
                )
                orthic_image.save(img_path)

                # if big, create a thumbnail to dislay in the window
                thumbnail = create_thumbnail(orthic_image)
                thumbnail_path = "temp_thumbnail.png"
                thumbnail.save(thumbnail_path)

                # display the thumbnail
                window["-IMAGE-"].update(filename=thumbnail_path)

                # show/hide text about image having been resized
                if (
                    thumbnail.width == orthic_image.width
                    and thumbnail.height == orthic_image.height
                ):
                    window["-INFO-"].update(visible=False)
                else:
                    window["-INFO-"].update(visible=True)
            else:
                sg.Popup("Enter some text to transcribe.", title="Error")
        elif event == "Open in Viewer":
            if orthic_image:
                orthic_image.show()
            else:
                sg.popup(
                    "No image to display. Please transcribe text first.", title="Error"
                )
        elif event == "Export to PDF":
            # Optimize format for Kindle
            PADDING_SIZE = 20
            KINDLE_HEIGHT = 1024  # 1448
            KINDLE_WIDTH = 768  # 1072
            line_height = 100
            DPI = 212  # 300

            text = values["-INPUT-"]
            images = GlyphRenderer().render_text(
                text,
                line_width=KINDLE_WIDTH - PADDING_SIZE,
                line_height=line_height,
                lines_per_page=(KINDLE_HEIGHT - PADDING_SIZE) // line_height,
            )

            # Convert and expand PIL Images for saving as PDF
            pdf_images = [
                expand_canvas(
                    img.convert("RGB"), KINDLE_WIDTH, KINDLE_HEIGHT, PADDING_SIZE
                )
                for img in images
            ]

            # Save as a PDF
            pdf_filename = "transcription.pdf"
            pdf_images[0].save(
                pdf_filename,
                save_all=True,
                append_images=pdf_images[1:],
                dpi=(DPI, DPI),
            )

            sg.popup(
                f"Exported to PDF successfully!\n\nFile: {pdf_filename}",
                title="Export Complete",
            )
        elif event == "About":
            sg.popup(
                "text2orthic: Orthic Shorthand Transcriptor\n\nCreated by rmattila\nhttps://github.com/rmattila/text2orthic",
                title="About",
            )

    window.close()


if __name__ == "__main__":
    main()
