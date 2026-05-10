
from django import forms
from .models import Order


QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 11)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
        choices=QUANTITY_CHOICES,
        coerce=int,
        label="الكمية",
        widget=forms.Select(attrs={
            'class': 'form-control text-center m-0',
            'style': 'width: 65px; padding: 5px; cursor: pointer;'
        })
    )

    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'city', 'address', 'notes']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address (Optional)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City / Governorate'}),
            'address': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Enter detailed address here...', 'rows': 3}),
            'notes': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Any additional notes for shipping (Optional)',
                       'rows': 2}),
        }