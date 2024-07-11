"""Templates for the Thermal Printer integration."""

TEMPLATES = {
    "kanban": (
        "# KANBAN CARD\n\n"
        "## Title: {title}\n"
        "Description: {description}\n"
        "Priority: {priority}\n"
        "Assignee: {assignee}\n"
    ),
    "inquiry": (
        "# INQUIRY FORM\n\n"
        "Name: {name}\n"
        "Phone: {phone}\n"
        "Date: {date}\n"
        "Notes: {notes}\n"
    ),
    # Add more templates as needed
}


def get_template(name):
    """Get a template by name."""
    return TEMPLATES.get(name, "{content}")  # Default to plain content if template not found
