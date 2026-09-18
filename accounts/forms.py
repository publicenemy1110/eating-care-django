from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import PatientProfile, PsychologistProfile, User, UserRole


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'auth-form__input', 'placeholder': 'Email'}),
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'auth-form__input', 'placeholder': 'Имя'}),
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'auth-form__input', 'placeholder': 'Фамилия'}),
    )
    role = forms.ChoiceField(
        label='Я регистрируюсь как',
        choices=(
            (UserRole.PATIENT, UserRole.PATIENT.label),
            (UserRole.PSYCHOLOGIST, UserRole.PSYCHOLOGIST.label),
        ),
        widget=forms.Select(attrs={'class': 'auth-form__input'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'auth-form__input', 'placeholder': 'Логин'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'auth-form__input',
            'placeholder': 'Пароль',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'auth-form__input',
            'placeholder': 'Повторите пароль',
        })
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['role'].help_text = (
            'Регистрация как психолог требует проверки администратором. '
            'После регистрации заполните профессиональный профиль и дождитесь одобрения.'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'profile-form__input', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'profile-form__input', 'placeholder': 'Фамилия'}),
            'email': forms.EmailInput(attrs={'class': 'profile-form__input', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'profile-form__input', 'placeholder': '+7 (999) 000-00-00'}),
        }


class PsychologistProfileForm(forms.ModelForm):
    class Meta:
        model = PsychologistProfile
        fields = ('specialization', 'license_number', 'bio', 'is_accepting_patients')
        widgets = {
            'specialization': forms.TextInput(
                attrs={'class': 'profile-form__input', 'placeholder': 'Например: РПП, КПТ'},
            ),
            'license_number': forms.TextInput(
                attrs={'class': 'profile-form__input', 'placeholder': 'Номер лицензии'},
            ),
            'bio': forms.Textarea(
                attrs={
                    'class': 'profile-form__textarea',
                    'placeholder': 'Расскажите о своём опыте и подходе к работе',
                    'rows': 5,
                },
            ),
            'is_accepting_patients': forms.CheckboxInput(attrs={'class': 'profile-form__checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['specialization'].required = True
        self.fields['license_number'].required = True


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ('date_of_birth', 'emergency_contact')
        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={'class': 'profile-form__input', 'type': 'date'},
            ),
            'emergency_contact': forms.TextInput(
                attrs={'class': 'profile-form__input', 'placeholder': 'Имя и телефон близкого человека'},
            ),
        }
