"""
Live preview renderer.
Generates HTML preview for the builder interface.
"""
from flask import render_template


def render_preview(cv, template_slug):
    """
    Render CV preview HTML.

    Args:
        cv: CV model instance
        template_slug: Template identifier

    Returns:
        str: Rendered HTML content
    """
    # TODO: Implement in Phase 1
    # return render_template(f'cv_templates/{template_slug}.html', cv=cv)
    pass
