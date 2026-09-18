from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Администратор'
    PSYCHOLOGIST = 'psychologist', 'Психолог'
    PATIENT = 'patient', 'Пациент'


class PsychologistModerationStatus(models.TextChoices):
    PENDING = 'pending', 'На модерации'
    APPROVED = 'approved', 'Одобрен'
    REJECTED = 'rejected', 'Отклонён'


class User(AbstractUser):
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.PATIENT,
    )
    phone = models.CharField('Телефон', max_length=20, blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_admin_role(self):
        return self.role == UserRole.ADMIN

    @property
    def is_psychologist(self):
        return self.role == UserRole.PSYCHOLOGIST

    @property
    def is_approved_psychologist(self):
        if not self.is_psychologist:
            return False
        profile = PsychologistProfile.objects.filter(user=self).first()
        return profile is not None and profile.moderation_status == PsychologistModerationStatus.APPROVED

    @property
    def is_patient(self):
        return self.role == UserRole.PATIENT


class PsychologistProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='psychologist_profile',
        limit_choices_to={'role': UserRole.PSYCHOLOGIST},
        verbose_name='Пользователь',
    )
    specialization = models.CharField('Специализация', max_length=255, blank=True)
    license_number = models.CharField('Номер лицензии', max_length=100, blank=True)
    bio = models.TextField('О себе', blank=True)
    is_accepting_patients = models.BooleanField('Принимает пациентов', default=True)
    moderation_status = models.CharField(
        'Статус модерации',
        max_length=20,
        choices=PsychologistModerationStatus.choices,
        default=PsychologistModerationStatus.PENDING,
    )
    moderation_note = models.TextField('Комментарий модератора', blank=True, default='')
    moderated_at = models.DateTimeField('Дата модерации', null=True, blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True)

    class Meta:
        verbose_name = 'Профиль психолога'
        verbose_name_plural = 'Профили психологов'

    def __str__(self):
        return f'Психолог: {self.user}'

    @property
    def is_approved(self):
        return self.moderation_status == PsychologistModerationStatus.APPROVED


class PatientProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient_profile',
        limit_choices_to={'role': UserRole.PATIENT},
        verbose_name='Пользователь',
    )
    psychologist = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients',
        limit_choices_to={'role': UserRole.PSYCHOLOGIST},
        verbose_name='Психолог',
    )
    date_of_birth = models.DateField('Дата рождения', null=True, blank=True)
    emergency_contact = models.CharField('Контакт для экстренной связи', max_length=255, blank=True)
    notes = models.TextField('Заметки', blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True)

    class Meta:
        verbose_name = 'Профиль пациента'
        verbose_name_plural = 'Профили пациентов'

    def __str__(self):
        return f'Пациент: {self.user}'
