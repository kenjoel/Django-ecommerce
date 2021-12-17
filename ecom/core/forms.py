from django import forms
from django_countries.fields import CountryField

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField()
    apartment_address = forms.CharField(required=False)
    country = CountryField(blank_label='(select country)').formfield()
    zip = forms.CharField()
    same_shipping_address = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    save_info = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Promo code'}))
