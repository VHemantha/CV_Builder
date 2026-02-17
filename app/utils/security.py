"""
Security utilities.
CSP headers, sanitization helpers, etc.
"""
import bleach


ALLOWED_TAGS = ["b", "i", "u", "strong", "em", "ul", "ol", "li", "a", "br", "p"]
ALLOWED_ATTRIBUTES = {"a": ["href", "title"]}


def sanitize_html(content):
    """
    Sanitize HTML content to prevent XSS.

    Args:
        content: Raw HTML string

    Returns:
        Sanitized HTML string
    """
    return bleach.clean(
        content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True
    )


def validate_url(url, allowed_schemes=None):
    """
    Validate URL against allowed schemes.

    Args:
        url: URL string to validate
        allowed_schemes: List of allowed schemes (default: ['http', 'https', 'mailto'])

    Returns:
        bool: True if valid, False otherwise
    """
    if allowed_schemes is None:
        allowed_schemes = ["http", "https", "mailto"]

    from urllib.parse import urlparse

    try:
        result = urlparse(url)
        return result.scheme in allowed_schemes
    except Exception:
        return False
