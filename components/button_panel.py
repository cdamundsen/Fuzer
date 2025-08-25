import os
from winup import ui, component, state
from Fuzer import run_fuzer

selected_mp3_files = state.create("selected_mp3_files")
selected_jpg_file = state.create("selected_jpg_file")
current_directory = state.create("current_directory")
input_files = state.create("input_files")
cover_file = state.create("cover_file")
messages = state.create("messages")


@component
def ButtonPanel() -> ui.Column:
    def on_mp3_button_click() -> None:
        files = selected_mp3_files.get()
        cur_dir = current_directory.get()
        input_files.set(
            sorted(
                [
                    cur_dir + x
                    for x in files
                    if os.path.splitext(x)[-1].upper() == ".MP3"
                ]
            )
        )

    def on_clear_mp3_button() -> None:
        input_files.set([])

    def on_image_button_click() -> None:
        image_file = selected_jpg_file.get()

        cur_dir = current_directory.get()
        if os.path.splitext(image_file)[-1].upper() not in (".JPG", ".JPEG"):
            print(f"Only jpeg files supported: {image_file}")
        else:
            cover_file.set(cur_dir + image_file)

    def on_clear_image_button_click() -> None:
        cover_file.set("Select a jpeg for the cover...")

    def make_book() -> None:
        destination_dir = current_directory.get()
        mp3_files = input_files.get()
        cover_image = cover_file.get()
        cover_image = open(cover_image, "rb") if os.path.isfile(cover_image) else None

        msg = run_fuzer(mp3_files, cover=cover_image, dest_dir=destination_dir, raise_exceptions=False)
        if msg:
            messages.set(msg)

    clear_mp3_button_props = (
        {"class": "add-button-disabled"}
        if input_files.get() == []
        else {"class": "add-button"}
    )
    clear_cover_image_props = (
        {"class": "add-button-disabled"}
        if cover_file.get() == "Select a jpeg for the cover..."
        else {"class": "add-button"}
    )

    return ui.Column(
        children=[
            ui.Button(
                "cover image --->",
                on_click=lambda: on_image_button_click(),
                props={"class": "add-button"},
            ),
            ui.Button(
                "Clear cover image",
                on_click=lambda: on_clear_image_button_click(),
                props=clear_cover_image_props,
            ),
            ui.Button(
                "mp3 files --->",
                on_click=lambda: on_mp3_button_click(),
                props={"class": "add-button"},
            ),
            ui.Button(
                "Clear mp3 files",
                on_click=lambda: on_clear_mp3_button(),
                props=clear_mp3_button_props,
            ),
            ui.Button(
                "Make book", on_click=lambda: make_book(), props=clear_mp3_button_props
            ),
        ]
    )
