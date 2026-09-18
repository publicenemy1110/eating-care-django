from django import forms
from django.forms import inlineformset_factory

from .models import CustomQuestion, CustomTest


class CustomTestForm(forms.ModelForm):
    class Meta:
        model = CustomTest
        fields = ('title', 'short_description', 'instructions', 'answer_type', 'is_published')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'custom-test-form__input',
                'placeholder': 'Название опросника',
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'custom-test-form__textarea',
                'placeholder': 'Кратко опишите, для чего предназначен тест',
                'rows': 3,
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'custom-test-form__textarea',
                'placeholder': 'Инструкция для прохождения (необязательно)',
                'rows': 3,
            }),
            'answer_type': forms.Select(attrs={'class': 'custom-test-form__input'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'custom-test-form__checkbox'}),
        }
        labels = {
            'is_published': 'Сразу опубликовать для пациентов',
        }


class CustomQuestionForm(forms.ModelForm):
    class Meta:
        model = CustomQuestion
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'custom-test-form__textarea',
                'placeholder': 'Текст вопроса',
                'rows': 2,
            }),
        }


CustomQuestionFormSet = inlineformset_factory(
    CustomTest,
    CustomQuestion,
    form=CustomQuestionForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
)
