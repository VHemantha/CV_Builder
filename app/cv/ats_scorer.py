"""
ATS (Applicant Tracking System) score calculator.
Analyzes CV content and provides optimization suggestions.
"""


def calculate_ats_score(cv):
    """
    Calculate ATS-friendliness score (0-100).

    Scoring factors:
    - Section presence (contact, summary, experience, education, skills)
    - Keyword density and action verbs
    - Date formatting consistency
    - Bullet point usage
    - No problematic elements (images, tables in ATS mode)

    Args:
        cv: CV model instance

    Returns:
        dict: {
            'score': int (0-100),
            'breakdown': dict of individual scores,
            'suggestions': list of improvement tips
        }
    """
    # TODO: Implement in Phase 2
    pass


def get_improvement_suggestions(cv):
    """
    Get specific suggestions to improve ATS score.

    Returns:
        list: Actionable tips (max 5)
    """
    # TODO: Implement in Phase 2
    pass
