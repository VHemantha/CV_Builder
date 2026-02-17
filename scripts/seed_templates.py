"""
Seed database with CV template metadata.
Run with: flask seed-templates
"""


def seed():
    """Populate CV templates in database."""
    from app import create_app
    from app.extensions import db

    app = create_app()

    with app.app_context():
        print("Seeding CV templates...")

        # TODO: Implement template model and seeding
        # For now, templates will be static files
        # In future, can create a CVTemplate model for metadata

        templates = [
            {
                "slug": "ats_clean",
                "name": "ATS Clean",
                "category": "ats",
                "description": "Single-column, no graphics, standard headings",
                "is_ats_friendly": True,
                "sort_order": 1,
            },
            {
                "slug": "ats_modern",
                "name": "ATS Modern",
                "category": "ats",
                "description": "Single-column, subtle accent color, clean dividers",
                "is_ats_friendly": True,
                "sort_order": 2,
            },
            {
                "slug": "ats_executive",
                "name": "ATS Executive",
                "category": "ats",
                "description": "Classic two-column header, single-column body",
                "is_ats_friendly": True,
                "sort_order": 3,
            },
            {
                "slug": "pro_elegant",
                "name": "Professional Elegant",
                "category": "professional",
                "description": "Cream paper tone, refined typography, tasteful icons",
                "is_ats_friendly": False,
                "sort_order": 4,
            },
            {
                "slug": "pro_creative",
                "name": "Professional Creative",
                "category": "professional",
                "description": "Accent sidebar with skills bars, photo slot",
                "is_ats_friendly": False,
                "sort_order": 5,
            },
            {
                "slug": "pro_bold",
                "name": "Professional Bold",
                "category": "professional",
                "description": "High-contrast header, card-style entries",
                "is_ats_friendly": False,
                "sort_order": 6,
            },
        ]

        print(f"Defined {len(templates)} templates")
        print("✓ Templates ready (stored as static files)")

        # In Phase 1, templates are just HTML/CSS files
        # No database entries needed yet
        # Can add CVTemplate model in Phase 2 if dynamic template management is needed


if __name__ == "__main__":
    seed()
