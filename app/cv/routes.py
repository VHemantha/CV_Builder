"""
CV management routes.
Dashboard, editor, preview, and download endpoints.
"""
from flask import render_template, redirect, url_for, flash, abort, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from app.cv import bp
from app.extensions import db, limiter
from app.models import CV, CVSection, DownloadLog
import uuid


@bp.route("/dashboard")
def dashboard():
    """Display user's CV dashboard."""
    if current_user.is_authenticated:
        cvs = CV.query.filter_by(
            user_id=current_user.id,
            is_deleted=False
        ).order_by(CV.updated_at.desc()).all()
    else:
        # Guest users see empty dashboard
        cvs = []

    return render_template(
        "dashboard/index.html",
        cvs=cvs,
        max_cvs=current_app.config["MAX_CVS_PER_USER"]
    )


@bp.route("/new", methods=["POST"])
@login_required
def create_cv():
    """Create a new CV (requires authentication)."""
    title = request.form.get("title", "").strip()
    template_slug = request.form.get("template_slug", "ats_clean")

    if not title:
        flash("CV title is required.", "error")
        return redirect(url_for("cv.dashboard"))

    # Check CV limit
    if not current_user.can_create_cv(current_app.config["MAX_CVS_PER_USER"]):
        flash(f"You have reached the maximum limit of {current_app.config['MAX_CVS_PER_USER']} CVs.", "error")
        return redirect(url_for("cv.dashboard"))

    # Create new CV for logged-in user
    cv = CV(
        user_id=current_user.id,
        title=title,
        template_slug=template_slug,
        primary_color="#4285f4"  # Default blue
    )

    # Add default personal info section
    personal_section = CVSection(
        cv=cv,
        section_type="personal",
        label="Personal Information",
        content={
            "name": "",
            "email": current_user.email,
            "phone": "",
            "location": "",
            "linkedin": "",
            "github": "",
            "portfolio": "",
            "headline": ""
        },
        display_order=0
    )

    db.session.add(cv)
    db.session.add(personal_section)
    db.session.commit()

    flash(f"CV '{title}' created successfully!", "success")
    return redirect(url_for("cv.edit_cv", cv_id=cv.id))


@bp.route("/<cv_id>/edit")
def edit_cv(cv_id):
    """CV builder/editor interface (public access)."""
    cv = CV.query.get_or_404(cv_id)

    if cv.is_deleted:
        abort(404)

    return render_template("builder/editor.html", cv=cv)


@bp.route("/<cv_id>/delete", methods=["POST"])
@login_required
def delete_cv(cv_id):
    """Soft delete a CV (requires authentication)."""
    cv = CV.query.get_or_404(cv_id)

    # Verify ownership
    if cv.user_id != current_user.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    # Soft delete
    cv.soft_delete()

    return jsonify({"success": True})


@bp.route("/<cv_id>/preview")
@limiter.limit("120/minute")
def preview_cv(cv_id):
    """Live preview endpoint (rendered HTML) - public access."""
    cv = CV.query.get_or_404(cv_id)

    if cv.is_deleted:
        abort(404)

    # Render CV template
    template_name = f"cv_templates/{cv.template_slug}.html"

    try:
        return render_template(template_name, cv=cv)
    except Exception as e:
        return f"<p>Error rendering preview: {str(e)}</p>", 500


@bp.route("/<cv_id>/download")
@login_required
@limiter.limit("5/hour")
def download_cv(cv_id):
    """Generate and download PDF (requires authentication)."""
    from app.cv.pdf_generator import generate_pdf
    from datetime import datetime
    import io

    cv = CV.query.get_or_404(cv_id)

    # Verify ownership
    if cv.user_id != current_user.id:
        flash("You can only download your own CVs.", "error")
        abort(403)

    try:
        # Generate PDF
        pdf_bytes = generate_pdf(cv, cv.template_slug)

        # Log download with current user
        DownloadLog.create_log(
            cv=cv,
            user=current_user,
            ip_address=request.remote_addr,
            salt=current_app.config["IP_HASH_SALT"]
        )

        # Generate filename
        # Get personal info for name
        personal_section = cv.sections.filter_by(section_type="personal").first()
        if personal_section and personal_section.content.get("name"):
            name = personal_section.content["name"].replace(" ", "_")
        else:
            name = cv.title.replace(" ", "_")

        filename = f"{name}_CV_{datetime.now().strftime('%Y-%m')}.pdf"

        return send_file(
            pdf_bytes,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )

    except RuntimeError as e:
        # WeasyPrint not available
        flash(str(e), "error")
        flash("Tip: You can still use the preview and print to PDF from your browser!", "info")
        return redirect(url_for("cv.edit_cv", cv_id=cv_id))
    except Exception as e:
        current_app.logger.error(f"PDF generation failed: {e}")
        flash("Failed to generate PDF. Please try again.", "error")
        return redirect(url_for("cv.edit_cv", cv_id=cv_id))


# ============================================
# API Endpoints for Section Management
# ============================================

@bp.route("/api/<cv_id>/sections", methods=["GET"])
def get_sections(cv_id):
    """Get all sections for a CV (public access)."""
    cv = CV.query.get_or_404(cv_id)

    sections = cv.sections.order_by(CVSection.display_order).all()
    return jsonify({
        "sections": [section.to_dict() for section in sections]
    })


@bp.route("/api/<cv_id>/sections", methods=["POST"])
@login_required
def create_section(cv_id):
    """Create a new section (requires authentication)."""
    cv = CV.query.get_or_404(cv_id)

    # Verify ownership
    if cv.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    section = CVSection(
        cv_id=cv.id,
        section_type=data.get("section_type"),
        label=data.get("label"),
        content=data.get("content", {}),
        display_order=data.get("display_order", 999)
    )

    db.session.add(section)
    db.session.commit()

    return jsonify({
        "success": True,
        "section": section.to_dict()
    })


@bp.route("/api/<cv_id>/sections/<section_id>", methods=["PUT"])
@login_required
def update_section(cv_id, section_id):
    """Update an existing section (requires authentication)."""
    cv = CV.query.get_or_404(cv_id)

    # Verify ownership
    if cv.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    section = CVSection.query.get_or_404(section_id)

    if section.cv_id != cv.id:
        return jsonify({"error": "Invalid section"}), 400

    data = request.get_json()

    if "content" in data:
        section.content = data["content"]
    if "label" in data:
        section.label = data["label"]
    if "is_visible" in data:
        section.is_visible = data["is_visible"]
    if "display_order" in data:
        section.display_order = data["display_order"]

    db.session.commit()

    return jsonify({
        "success": True,
        "section": section.to_dict()
    })


@bp.route("/api/<cv_id>/sections/<section_id>", methods=["DELETE"])
@login_required
def delete_section(cv_id, section_id):
    """Delete a section (requires authentication)."""
    cv = CV.query.get_or_404(cv_id)

    # Verify ownership
    if cv.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    section = CVSection.query.get_or_404(section_id)

    if section.cv_id != cv.id:
        return jsonify({"error": "Invalid section"}), 400

    db.session.delete(section)
    db.session.commit()

    return jsonify({"success": True})


@bp.route("/api/<cv_id>/meta", methods=["PUT"])
@login_required
def update_meta(cv_id):
    """Update CV metadata (requires authentication)."""
    cv = CV.query.get_or_404(cv_id)

    # Verify ownership
    if cv.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    if "title" in data:
        cv.title = data["title"]
    if "template_slug" in data:
        cv.template_slug = data["template_slug"]
    if "primary_color" in data:
        cv.primary_color = data["primary_color"]
    if "font_pair" in data:
        cv.font_pair = data["font_pair"]

    db.session.commit()

    return jsonify({
        "success": True,
        "cv": cv.to_dict()
    })
