from django import forms
from .models import Order


class CartAddProductForm(forms.Form):

    QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 4)]

    quantity = forms.TypedChoiceField(
        choices=QUANTITY_CHOICES,
        coerce=int,
        label="الكمية"
    )

    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'city', 'address', 'notes']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الأول'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الأخير'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف للتواصل'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني (اختياري)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'المدينة أو المحافظة'}),
            'address': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'أدخل العنوان بالتفصيل هنا...', 'rows': 3}),
            'notes': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'أي ملاحظات إضافية لشركة الشحن (اختياري)', 'rows': 2}),
        }