import re

from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User

from .models import ShippingAddress, UserProfile

FIELD_CLASS = "cc-input"
TEXTAREA_CLASS = "cc-textarea"
CHECKBOX_CLASS = "mr-2 align-middle"


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": FIELD_CLASS}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"class": FIELD_CLASS}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget = forms.PasswordInput(attrs={"class": FIELD_CLASS})
        self.fields["password2"].widget = forms.PasswordInput(attrs={"class": FIELD_CLASS})


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": FIELD_CLASS, "placeholder": "First name"},
            ),
            "last_name": forms.TextInput(
                attrs={"class": FIELD_CLASS, "placeholder": "Last name"},
            ),
            "email": forms.EmailInput(
                attrs={"class": FIELD_CLASS, "placeholder": "Email address"},
            ),
        }


class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("phone", "receive_order_updates", "receive_promotions")
        widgets = {
            "phone": forms.TextInput(
                attrs={"class": FIELD_CLASS, "placeholder": "10-digit mobile number"},
            ),
            "receive_order_updates": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "receive_promotions": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()

        if not phone:
            return ""

        phone = re.sub(r"\D", "", phone)

        if not re.match(r"^[6-9]\d{9}$", phone):
            raise forms.ValidationError("Enter a valid 10-digit Indian mobile number.")

        return phone


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = (
            "label",
            "full_name",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "pincode",
            "is_default",
        )
        widgets = {
            "label": forms.TextInput(
                attrs={"class": FIELD_CLASS, "placeholder": "Home, Office, etc."},
            ),
            "full_name": forms.TextInput(
                attrs={"class": FIELD_CLASS, "placeholder": "Full name"},
            ),
            "email": forms.EmailInput(
                attrs={"class": FIELD_CLASS, "placeholder": "Email"},
            ),
            "phone": forms.TextInput(
                attrs={"class": FIELD_CLASS, "placeholder": "Phone number"},
            ),
            "address": forms.Textarea(
                attrs={"class": TEXTAREA_CLASS, "placeholder": "Full address", "rows": 4},
            ),
            "city": forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "City"}),
            "state": forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "State"}),
            "pincode": forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "Pincode"}),
            "is_default": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
        }

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


class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": FIELD_CLASS})
