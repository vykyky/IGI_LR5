from django import forms
from .models import Review, Question, Answer, Vacancy, Category, Service
from users.models import DoctorCategory, DoctorSpecialization


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug'] 

class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        exclude = []


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ['date', 'answer']


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'image', 'category', 'available']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        exclude = ['date']


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  

    rate = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.Select(attrs={
            'required': True,
        })
    )

    class Meta:
        model = Review
        exclude = ['author', 'date']


