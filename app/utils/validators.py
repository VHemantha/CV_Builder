"""
Custom WTForms validators.
"""
from wtforms.validators import ValidationError
from app.utils.security import validate_url


class SafeURL:
    """
    Validates that URL uses allowed schemes.

    Usage:
        url = StringField('URL', validators=[SafeURL()])
    """

    def __init__(self, allowed_schemes=None, message=None):
        self.allowed_schemes = allowed_schemes or ["http", "https"]
        self.message = message

    def __call__(self, form, field):
        if field.data and not validate_url(field.data, self.allowed_schemes):
            message = self.message or f"URL must use one of: {', '.join(self.allowed_schemes)}"
            raise ValidationError(message)


class MaxWordsCount:
    """
    Validates maximum word count.

    Usage:
        description = TextAreaField('Description', validators=[MaxWordsCount(500)])
    """

    def __init__(self, max_words, message=None):
        self.max_words = max_words
        self.message = message

    def __call__(self, form, field):
        if field.data:
            word_count = len(field.data.split())
            if word_count > self.max_words:
                message = self.message or f"Maximum {self.max_words} words allowed (you have {word_count})"
                raise ValidationError(message)
