from django import forms
from .models import MyUser, Client, Doctor, DoctorSpecialization, DoctorCategory
from .mixins import ValidationMixin
from datetime import date
from django.core.exceptions import ValidationError

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ('username', 'email', 'first_name', 'last_name', 'patronymic', 'telephone')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'telephone': 'Телефон',
        }

class ClientRegistrationForm(forms.ModelForm, ValidationMixin):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput())
    birth_date = forms.DateField(label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Client
        fields = ('birth_date', 'address') 
        labels = {
            'address': 'Адрес',
        } 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_fields = UserRegistrationForm().fields
        self.fields.update(self.user_fields)
        self.order_fields([
            'username', 'email', 'last_name','first_name',  'patronymic', 'telephone',
            'birth_date', 'address', 'password1', 'password2'
        ])
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean(self):
        cleaned_data = super().clean()
        self.check_username(cleaned_data.get('username'))
        self.check_email(cleaned_data.get('email'))
        self.check_passwords(cleaned_data.get('password1'), cleaned_data.get('password2'))
        self.check_password_length(cleaned_data.get('password1'))
        self.check_telephone(cleaned_data.get('telephone'))

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                raise ValidationError("Регистрация доступна только с 18 лет.")
        return birth_date

class DoctorRegistrationForm(forms.ModelForm, ValidationMixin):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput())
    birth_date = forms.DateField(label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Doctor
        fields = ('birth_date', 'image', 'category', 'specialization', 'department', 'services')
        labels = {
            'image': 'Изображение',
            'category': 'Категория',
            'specialization': 'Специализация',
            'department': 'Отделение',
            'services': 'Услуги',
        } 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_fields = UserRegistrationForm().fields
        self.fields.update(self.user_fields)
        self.order_fields([
            'username', 'email', 'last_name', 'first_name', 'patronymic', 'telephone',
            'birth_date', 'image', 'category', 'specialization', 'department', 'services',
            'password1', 'password2'
        ])
        self.fields['services'].widget.attrs.update({'multiple': True})

        self.fields['services'].required = False
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean(self):
        cleaned_data = super().clean()
        self.check_username(cleaned_data.get('username'))
        self.check_email(cleaned_data.get('email'))
        self.check_passwords(cleaned_data.get('password1'), cleaned_data.get('password2'))
        self.check_password_length(cleaned_data.get('password1'))
        self.check_telephone(cleaned_data.get('telephone'))

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                raise ValidationError("Регистрация доступна только с 18 лет.")
        return birth_date


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')


class DoctorSpecializationForm(forms.ModelForm):
    class Meta:
        model = DoctorSpecialization
        exclude = []

class DoctorCategoryForm(forms.ModelForm):
    class Meta:
        model = DoctorCategory
        exclude = []

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['birth_date', 'image', 'category', 'specialization', 'department', 'services']