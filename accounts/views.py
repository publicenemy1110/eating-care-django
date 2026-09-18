from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import PatientProfileForm, PsychologistProfileForm, RegistrationForm, UserProfileForm
from .models import (
    PatientProfile,
    PsychologistModerationStatus,
    PsychologistProfile,
    User,
    UserRole,
)


class StyledLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = ''
        return context


class StyledLogoutView(LogoutView):
    next_page = reverse_lazy('pages:index')


def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.role == UserRole.PSYCHOLOGIST:
                messages.info(
                    request,
                    'Заявка на регистрацию психолога отправлена. '
                    'Заполните специализацию и номер лицензии — после проверки администратором '
                    'ваш профиль станет доступен пациентам.',
                )
            else:
                messages.success(request, 'Добро пожаловать! Заполните профиль.')
            return redirect('accounts:profile')

    return render(request, 'accounts/register.html', {
        'active_page': '',
        'form': form,
    })


def _get_role_label(user, role_profile):
    role_labels = dict(UserRole.choices)
    if user.role != UserRole.PSYCHOLOGIST or role_profile is None:
        return role_labels.get(user.role, user.role)
    if role_profile.moderation_status == PsychologistModerationStatus.PENDING:
        return 'Психолог — на модерации'
    if role_profile.moderation_status == PsychologistModerationStatus.REJECTED:
        return 'Психолог — заявка отклонена'
    return role_labels.get(user.role, user.role)


@login_required
def profile(request):
    user = request.user
    role_profile = None
    role_form = None

    if user.role == UserRole.PSYCHOLOGIST:
        role_profile, _ = PsychologistProfile.objects.get_or_create(
            user=user,
            defaults={
                'moderation_status': PsychologistModerationStatus.PENDING,
                'moderation_note': '',
            },
        )
        role_form_class = PsychologistProfileForm
    elif user.role == UserRole.PATIENT:
        role_profile, _ = PatientProfile.objects.get_or_create(user=user)
        role_form_class = PatientProfileForm
    else:
        role_form_class = None

    user_form = UserProfileForm(instance=user)
    if role_form_class:
        role_form = role_form_class(instance=role_profile)

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=user)
        forms_valid = user_form.is_valid()

        if role_form_class:
            role_form = role_form_class(request.POST, instance=role_profile)
            forms_valid = forms_valid and role_form.is_valid()

        if forms_valid:
            user_form.save()
            if role_form_class:
                was_rejected = (
                    user.role == UserRole.PSYCHOLOGIST
                    and role_profile.moderation_status == PsychologistModerationStatus.REJECTED
                )
                role_form.save()
                if was_rejected:
                    role_profile.moderation_status = PsychologistModerationStatus.PENDING
                    role_profile.moderation_note = ''
                    role_profile.moderated_at = None
                    role_profile.save(update_fields=['moderation_status', 'moderation_note', 'moderated_at'])
                    messages.info(request, 'Профиль отправлен на повторную модерацию.')
                else:
                    messages.success(request, 'Профиль успешно обновлён.')
            else:
                messages.success(request, 'Профиль успешно обновлён.')
            return redirect('accounts:profile')

    context = {
        'active_page': 'profile',
        'profile_user': user,
        'user_form': user_form,
        'role_form': role_form,
        'role_profile': role_profile,
        'role_label': _get_role_label(user, role_profile),
        'is_own_profile': True,
    }
    return render(request, 'accounts/profile.html', context)


def psychologist_public(request, username):
    user = get_object_or_404(User, username=username, role=UserRole.PSYCHOLOGIST)
    role_profile = get_object_or_404(
        PsychologistProfile,
        user=user,
        moderation_status=PsychologistModerationStatus.APPROVED,
    )
    context = {
        'active_page': '',
        'profile_user': user,
        'role_profile': role_profile,
        'role_label': UserRole.PSYCHOLOGIST.label,
        'is_own_profile': request.user.is_authenticated and request.user.pk == user.pk,
    }
    return render(request, 'accounts/profile.html', context)
