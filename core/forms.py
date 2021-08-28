from core.models import Address
from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


# class CheckoutForm(forms.ModelForm):
#     model = Address
#     street_address = forms.CharField(widget=forms.TextInput(attrs={
#         "placeholder": "1234 Main St",
#         "class": "form-control",
#     }))
#     appartment_address = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={
#             "placeholder": "Appartment or Suite",
#             "class": "form-control",
#         })
#     )
#     country = CountryField(blank_label='Select').formfield(
#         widget=CountrySelectWidget(attrs={
#             'class': 'custom-select d-block w-100',
#         })
#     )
#     state = forms.CharField(widget=forms.TextInput(attrs={
#         "placeholder": "California",
#         "class": "form-control",
#     }))
#     zip = forms.CharField(widget=forms.TextInput(attrs={
#         "class": "form-control",
#     }))
#     same_billing_address = forms.BooleanField(required=False)
#     save_info = forms.BooleanField(required=False)
#     payment_option = forms.ChoiceField(
#         widget=forms.RadioSelect, choices=PAYMENT_CHOICES)

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal'),
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        "placeholder": "1234 Main St",
        "class": "form-control",
    }))
    appartment_address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Appartment or Suite",
            "class": "form-control",
        })
    )
    country = CountryField(blank_label='Select').formfield(
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        })
    )
    state = forms.CharField(widget=forms.TextInput(attrs={
        "placeholder": "California",
        "class": "form-control",
    }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
    }))
    same_billing_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
