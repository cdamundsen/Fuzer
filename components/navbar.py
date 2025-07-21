from winup import ui, state, style, component

@component
def Navbar():
    """
    The main navication bar for the application
    """
    page_state = state.create("current_directory") # Get the existing state object

    def set_theme(theme_name):
        style.themes.set_theme(theme_name)

    theme_buttons = ui.Row(
            props={"alignment": "AlignmentRight"},
            children=[
                ui.Button(
                    "Light Mode",
                    on_click=lambda: set_theme("light")
                ),
                ui.Button(
                    "Dark Mode",
                    on_click=lambda: set_theme("dark")
                ),
            ]
    )

    return ui.Frame(
        props={
            "id": "navbar",
            "class": "header"
        },
        children=[
            ui.Row(
                props={"spacing": 10, "alignment": "AlignLeft"},
                children=[
                    (ui.Label("winFuzer", props={"class": "brand"}), {"stretch": 3}),
                    (theme_buttons, {"stretch": 1}),
                ]
            )
        ]
    )