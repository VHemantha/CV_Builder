"""
PDF generation using WeasyPrint.
"""
from flask import render_template
import io

# Try to import WeasyPrint, but make it optional
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    print(f"WeasyPrint not available: {e}")
    print("PDF generation will be disabled. App will still work!")


def generate_pdf(cv, template_slug):
    """
    Generate PDF from CV using specified template.

    Args:
        cv: CV model instance
        template_slug: Template identifier (e.g., 'ats_clean')

    Returns:
        BytesIO object containing PDF data

    Raises:
        RuntimeError: If WeasyPrint is not available
    """
    if not WEASYPRINT_AVAILABLE:
        raise RuntimeError(
            "PDF generation is not available. "
            "WeasyPrint requires GTK libraries which are not installed. "
            "See SETUP.md for installation instructions."
        )

    # Render HTML template with CV data
    template_name = f'cv_templates/{template_slug}.html'
    html_content = render_template(template_name, cv=cv)

    # Generate PDF with WeasyPrint
    pdf_bytes = HTML(string=html_content).write_pdf()

    # Return as BytesIO object
    return io.BytesIO(pdf_bytes)
