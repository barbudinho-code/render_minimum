"""
Form definition for post submission.

Validates:
- Email address format.
- Username length and format.
- Post text length limits.
"""

from django import forms


class SubmissionForm(forms.Form):
    """Form for submitting a new public post."""

    email = forms.EmailField(
        "Email address",
        max_length=254,
        help_text="We will send you a confirmation link via email.",
    )

    username = forms.CharField(
        "Username",
        min_length=2,
        max_length=40,
        help_text="A display name for your post (2-40 characters).",
    )

    text = forms.CharField(
        "Post text",
        widget=forms.Textarea(attrs={
            "rows": 6,
            "placeholder": "Write your post here...",
        }),
        min_length=1,
        max_length=3000,
        help_text="Your public post content (1-3000 characters).",
    )
