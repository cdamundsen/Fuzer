from winup import ui, component, state

messages = state.create("messages", "")


@component
def MessagesPanel() -> ui.ExpandablePanel:
    print(f"messages = -->{messages.get()}<--")
    label_strings = "" if not messages.get() else messages.get()
    panel_content = ui.Column(children=[ui.Label(label_strings)])

    return ui.ExpandablePanel(
        title="Status Messages",
        expanded=True if label_strings else False,
        children=[panel_content],
    )
