import re

from django import forms
from django.core.validators import RegexValidator


FIELD_CLASS = "cc-input"
TEXTAREA_CLASS = "cc-textarea"
CHECKBOX_CLASS = "mr-2 align-middle"


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        label="Full Name",
        min_length=2,
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": FIELD_CLASS, "placeholder": "Full Name", "required": True},
        ),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": FIELD_CLASS, "placeholder": "Email", "required": True},
        ),
    )
    phone = forms.CharField(
        label="Phone",
        max_length=15,
        widget=forms.TextInput(
            attrs={"class": FIELD_CLASS, "placeholder": "Phone Number", "required": True},
        ),
    )
    city = forms.CharField(
        label="City",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": FIELD_CLASS, "placeholder": "City", "required": True},
        ),
    )
    state = forms.CharField(
        label="State",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": FIELD_CLASS, "placeholder": "State", "required": True},
        ),
    )
    pincode = forms.CharField(
        label="Pincode",
        max_length=6,
        validators=[
            RegexValidator(
                regex=r"^\d{6}$",
                message="Enter a valid 6-digit pincode.",
            ),
        ],
        widget=forms.TextInput(
            attrs={"class": FIELD_CLASS, "placeholder": "Pincode", "required": True},
        ),
    )
    address = forms.CharField(
        label="Address",
        min_length=10,
        widget=forms.Textarea(
            attrs={
                "class": TEXTAREA_CLASS,
                "placeholder": "Full Address",
                "rows": 4,
                "required": True,
            }
        ),
    )
    save_address = forms.BooleanField(
        label="Save address",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
    )
    address_label = forms.CharField(
        label="Address label",
        required=False,
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": FIELD_CLASS,
                "placeholder": "Address label (e.g. Home, Office)",
            },
        ),
    )

    def clean_full_name(self):
        return self.cleaned_data["full_name"].strip()

    def clean_phone(self):
        phone = re.sub(r"\D", "", self.cleaned_data["phone"])

        if not re.match(r"^[6-9]\d{9}$", phone):
            raise forms.ValidationError("Enter a valid 10-digit Indian mobile number.")

        return phone

    def clean_pincode(self):
        pincode = self.cleaned_data["pincode"].strip()

        if not re.match(r"^\d{6}$", pincode):
            raise forms.ValidationError("Enter a valid 6-digit pincode.")

        return pincode

    def clean_address(self):
        return self.cleaned_data["address"].strip()

    def clean_address_label(self):
        label = self.cleaned_data.get("address_label", "").strip()

        if self.cleaned_data.get("save_address") and not label:
            return "Home"

        return label
