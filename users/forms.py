from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        help_text='Обязательное поле. Введите номер телефона.'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        help_text='Повторите пароль для подтверждения.'
    )

    class Meta:
        model = CustomUser
        fields = ('phone_number', 'password1', 'password2')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('Данный номер телефона уже зарегистрирован.')
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают.')

        return cleaned_data


class CustomAuthenticationForm(forms.Form):
    phone_number = forms.CharField(max_length=20, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
