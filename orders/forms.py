from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"class": "glass-card p-4 w-full", "placeholder": "Full Name"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "glass-card p-4 w-full", "placeholder": "Email"}),
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"class": "glass-card p-4 w-full", "placeholder": "Phone Number"}),
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "glass-card p-4 w-full", "placeholder": "City"}),
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "glass-card p-4 w-full", "placeholder": "State"}),
    )
    pincode = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"class": "glass-card p-4 w-full", "placeholder": "Pincode"}),
    )
    address = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "glass-card p-4 w-full",
                "placeholder": "Full Address",
                "rows": 4,
            }
        ),
    )
