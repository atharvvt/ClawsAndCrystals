from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):

    class Meta:

        model = Review

        fields = (
            "rating",
            "comment",
        )

        widgets = {

            "rating": forms.Select(
                attrs={
                    "class": "w-full border rounded-lg p-3"
                }
            ),

            "comment": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "w-full border rounded-lg p-3"
                }
            ),
        }