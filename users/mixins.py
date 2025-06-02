import re
from django.forms import ValidationError
from datetime import datetime
from .models import MyUser


class ValidationMixin:
    def check_username(self, username: str) -> str:
        if MyUser.objects.filter(username=username).exists():
            self.add_error('username', "Пользователь с таким именем уже существует.")
        return username
    
    def check_email(self, email: str) -> str:
        if MyUser.objects.filter(email=email).exists():
            self.add_error('email', "Пользователь с таким email уже существует.")
        return email

    def check_passwords(self, password1: str, password2: str) -> str:
        if password1 != password2:
            self.add_error('password2',"Пароли не совпадают")
        return password2

    def check_password_length(self, password1) -> str:
        if len(password1) < 8:
            self.add_error('password1',"Password len must be at least 8 letters or numbers")
        return password1

    def check_telephone(self, telephone: str) -> str:
        regex = r'\+375[0-9][0-9]\d{7}\b'
        if re.match(regex, telephone):
            return telephone

        self.add_error('telephone', "Введите корректный номер телефона в формате +375********.")

    def check_datetime(self, form_datetime):
        if form_datetime is None:
            raise ValidationError("The datetime cannot be none.")
        if form_datetime < datetime.now():
            raise ValidationError("The datetime cannot be in the past.")
        return form_datetime
