from django import forms

from .models import Review

FIELD_CLASS = "cc-input"
TEXTAREA_CLASS = "cc-textarea"


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ("rating", "comment")
        widgets = {
            "rating": forms.RadioSelect(
                attrs={"class": "review-form__rating-input"},
            ),
            "comment": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": TEXTAREA_CLASS,
                    "placeholder": "Share your experience with this piece…",
                },
            ),
        }
        labels = {
            "rating": "Your rating",
            "comment": "Your review",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rating"].required = True
        self.fields["comment"].required = True
