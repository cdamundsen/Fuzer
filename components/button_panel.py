import os
from winup import ui, component, state
from Fuzer import run_fuzer

selected_mp3_files = state.create("selected_mp3_files")
selected_jpg_file = state.create("selected_jpg_file")
current_directory = state.create("current_directory")
input_files = state.create("input_files")
cover_file = state.create("cover_file")

@component
def ButtonPanel():
    def on_mp3_button_click():
        files = selected_mp3_files.get()
        cur_dir = current_directory.get()
        input_files.set(sorted([cur_dir + x for x in files if os.path.splitext(x)[-1].upper() == '.MP3']))

    def on_clear_mp3_button():
        input_files.set([])

    def on_image_button_click():
        image_file = selected_jpg_file.get()

        cur_dir = current_directory.get()
        if os.path.splitext(image_file)[-1].upper() not in ('.JPG', '.JPEG'):
            print(f"Only jpeg files supported: {image_file}")
        else:
            cover_file.set(cur_dir + image_file)
    
    def on_clear_image_button_click():
        cover_file.set("Select a jpeg for the cover...")

    def make_book():
        destination_dir = current_directory.get()
        mp3_files = input_files.get()
        cover_image = cover_file.get()
        cover_image = open(cover_image, 'rb') if os.path.isfile(cover_image) else None
        title = None
        file_order = False

        print(f"-------> destination_dir = {destination_dir}")
        print(f"-------> type(destination_dir) = {type(destination_dir)}")
        print(f"-------> mp3_files = {mp3_files}")
        print(f"-------> type(mp3_files) = {type(mp3_files)}")
        print(f"-------> cover_image = {cover_image}")
        print(f"-------> type(cover_image) = {type(cover_image)}")
        print(f"-------> title = {title}")
        print(f"-------> type(title) = {type(title)}")
        print(f"-------> file_order = {file_order}")
        print(f"-------> type(file_order) = {type(file_order)}")
        run_fuzer(mp3_files, cover=cover_image, dest_dir=destination_dir)
    

    return ui.Column(
        children=[
            ui.Button("cover image --->", on_click=lambda: on_image_button_click(), props={"class": "add-button"}),
            ui.Button("Clear cover image", on_click=lambda: on_clear_image_button_click(), props={"class": "add-button"}),
            ui.Button("mp3 files --->", on_click=lambda: on_mp3_button_click(), props={"class": "add-button"}),
            ui.Button("Clear mp3 files", on_click=lambda: on_clear_mp3_button(), props={"class": "add-button"}),
            ui.Button("Make book", on_click=lambda: make_book(), props={"class": "add-button"}),
        ]
    )