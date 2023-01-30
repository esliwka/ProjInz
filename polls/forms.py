from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model

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




class UserCreationForm(forms.ModelForm):
    
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control','style': 'width: 40%', 'placeholder': 'Email'}))
    first_name = forms.CharField(label='Imię', widget=forms.TextInput(attrs={'class': 'form-control','style': 'width: 40%', 'placeholder': 'Imię'}))
    last_name = forms.CharField(label='Nazwisko', widget=forms.TextInput(attrs={'class': 'form-control','style': 'width: 40%', 'placeholder': 'Nazwisko'}))
    password1 = forms.CharField(label='Hasło', widget=forms.PasswordInput(attrs={'class': 'form-control','style': 'width: 40%', 'placeholder': 'Hasło'}))
    password2 = forms.CharField(label='Powtórz hasło', widget=forms.PasswordInput(attrs={'class': 'form-control','style': 'width: 40%', 'placeholder': 'Powtórz hasło'}))

    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
        labels = {
            'email': 'Email',
            'first_name': 'Imię',
            'last_name': 'Nazwisko',
            'password1': 'Hasło',
            'password2': 'Powtórz hasło',
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Hasła nie są zgodne.")
        return password2
    
    def clean_email(self):
        CustomUser = get_user_model()
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Podany email jest już zajęty.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class DateForm(forms.Form):
    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )