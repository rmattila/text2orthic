import PySimpleGUI as sg
from orthic_encoder import OrthicEncoder
from glyph_renderer import GlyphRenderer


def render_orthic_text(text):
    renderer = GlyphRenderer()
    return renderer.render_text(text)


def create_thumbnail(image, max_size=(580, 200)):
    thumbnail = image.copy()
    thumbnail.thumbnail(max_size)
    return thumbnail


def main():
    layout = [
        [sg.Text("Enter text to transcribe:")],
        [sg.Multiline(key="-INPUT-", size=(80, 20))],
        [
            sg.Button("Transcribe"),
            sg.Button("Open in Viewer"),
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
                orthic_image = render_orthic_text(text)
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
        elif event == "About":
            sg.popup(
                "text2orthic: Orthic Shorthand Transcriptor\n\nCreated by rmattila\nhttps://github.com/rmattila/text2orthic",
                title="About",
            )

    window.close()


if __name__ == "__main__":
    main()
