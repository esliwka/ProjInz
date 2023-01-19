from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.contrib import messages


class PolishPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Stare hasło", widget=forms.PasswordInput(attrs={'style': 'width: 40%'}))
    new_password1 = forms.CharField(label="Nowe hasło", widget=forms.PasswordInput(attrs={'style': 'width: 40%'}))
    new_password2 = forms.CharField(label="Powtórz nowe hasło", widget=forms.PasswordInput(attrs={'style': 'width: 40%'}))

    error_messages = {
        'password_incorrect': "Stare hasło jest niepoprawne.",
        'password_mismatch': "Hasła nie są takie same.",
    }

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 8:
            raise forms.ValidationError("Hasło powinno zawierać co najmniej 8 znaków.")
        if password.isnumeric():
            raise forms.ValidationError("Hasło powinno nie być wyłącznie numeryczne.")
        if not any(x.isupper() for x in password):
            raise forms.ValidationError("Hasło powinno zawierać co najmniej jedną wielką literę.")
        if not any(x.islower() for x in password):
            raise forms.ValidationError("Hasło powinno zawierać co najmniej jedną małą literę.")
        if not any(x.isnumeric() for x in password):
            raise forms.ValidationError("Hasło powinno zawierać co najmniej jedną cyfrę.")
        return password
