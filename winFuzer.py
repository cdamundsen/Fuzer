import winup
from winup import ui, state

import sys, os
from components.navbar import Navbar
from components.dir_tree_panel import TreeViewPanel
from components.file_panel import FilePanel
from components.input_files_panel import InputFilesPanel
from components.button_panel import ButtonPanel
import time

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from themes import apply_base_theme

input_files = state.create("input_files")
cover_file = state.create("cover_file")
current_directory = state.create("current_directory")

dir_label = ui.Label(text=current_directory.get()[-1])
current_directory.bind_to(
    dir_label,
    'text',
    lambda cd: f"Directory: {current_directory.get()[-1]}"
)

def App():
    # Set the themes
    apply_base_theme()

    file_list_container = ui.Frame(props={"id": "file_list_container", "layout": "vertical"})
    directory_tree_container = ui.Frame(props={"id": "directory_tree_container", "layout": "vertical"})
    input_files_container = ui.Frame(props={"id": "input_file_container", "layout": "vertical"})
    button_container = ui.Frame(props={"id": "button_container", "layout": "vertical"})

    def on_dir_change(cur_dir):
        ui.clear_layout(directory_tree_container.layout())
        ui.clear_layout(file_list_container.layout())

        directory_tree_container.add_child(TreeViewPanel())
        file_list_container.add_child(FilePanel())

    def on_input_file_change(input_files):
        ui.clear_layout(input_files_container.layout())
        input_files_container.add_child(InputFilesPanel())
        ui.clear_layout(button_container.layout())
        button_container.add_child(ButtonPanel())

    def on_cover_file_change(cover_file):
        ui.clear_layout(input_files_container.layout())
        input_files_container.add_child(InputFilesPanel())
        ui.clear_layout(button_container.layout())
        button_container.add_child(ButtonPanel())

    state.subscribe("current_directory", on_dir_change)
    state.subscribe("input_files", on_input_file_change)
    state.subscribe("cover_file", on_cover_file_change)

    on_dir_change(state.get("current_directory")) # Initial page load
    #button_container.add_child(ButtonPanel())

    return ui.Column(
        children=[
            Navbar(),
            ui.Row(
                children=[
                    directory_tree_container,
                    file_list_container,
                    button_container,
                    input_files_container,
                ]
            ),
        ]
    )

if __name__ == '__main__':
    winup.run(main_component_path="winFuzer:App", title="winFuzer", height=700, width=1000)
