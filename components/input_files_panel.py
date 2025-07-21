import os
from winup import ui, component, state

input_files = state.create("input_files", [])
cover_file = state.create("cover_file", "Select a jpeg for the cover...")

@component
def InputFilesPanel():

    return ui.Column(
        children=[
            ui.Label("Cover image", props={"class": "h1"}),
            ui.Label(cover_file.get(), props={"class": "QLabel"}),
            ui.Label("mp3 Files", props={"class": "h1"}),
            ui.List(
                items=[x.split(os.path.sep)[-1] for x in input_files.get()],
                multi_select=True,
                width=400,
                height=450
            ),

        ]
    )