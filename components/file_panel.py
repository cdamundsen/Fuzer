import os
from winup import ui, component, state

current_directory = state.create("current_directory")
selected_mp3_files = state.create("selected_mp3_files", [])
selected_jpg_file = state.create("selected_jpg_file", "")


@component
def FilePanel() -> ui.Column:
    cur_dir = state.get("current_directory")
    dir_items = [
        x for x in os.listdir(cur_dir) if x[0] != "."
    ]  # ingnore invisible files
    dir_items = sorted(
        [x for x in dir_items if os.path.isfile(cur_dir + x)]
    )  # Throw out directories
    mp3_items = [x for x in dir_items if os.path.splitext(x)[-1].upper() == ".MP3"]
    jpg_items = [
        x for x in dir_items if os.path.splitext(x)[-1].upper() in (".JPG", ".JPEG")
    ]

    def on_mp3_select(items:list[str]) -> None:
        selected_mp3_files.set(items)

    def on_jpg_select(item:str) -> None:
        selected_jpg_file.set(item)

    return ui.Column(
        children=[
            ui.Label(
                f"Current Directory:\n{current_directory.get().rstrip(os.path.sep).split(os.path.sep)[-1]}",
                props={"class": "h1"},
            ),
            ui.Label("jpeg files", props={"class": "h2"}),
            ui.List(
                items=jpg_items,
                multi_select=False,
                on_select=lambda item: on_jpg_select(item),
                width=250,
                # height=250
            ),
            ui.Label("mp3 files", props={"class": "h2"}),
            ui.List(
                items=mp3_items,
                multi_select=True,
                on_select=lambda items: on_mp3_select(items),
                width=250,
                # height=250
            ),
        ]
    )
