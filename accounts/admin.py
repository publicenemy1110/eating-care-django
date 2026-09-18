from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone

from .models import (
    PatientProfile,
    PsychologistModerationStatus,
    PsychologistProfile,
    User,
    UserRole,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'first_name', 'last_name', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('role', 'phone')}),
    )

    def save_model(self, request, obj, form, change):
        if obj.role == UserRole.ADMIN:
            obj.is_staff = True
        elif not change:
            obj.is_staff = False
        super().save_model(request, obj, form, change)


@admin.action(description='Одобрить выбранных психологов')
def approve_psychologists(modeladmin, request, queryset):
    now = timezone.now()
    updated = queryset.exclude(moderation_status=PsychologistModerationStatus.APPROVED).update(
        moderation_status=PsychologistModerationStatus.APPROVED,
        moderation_note='',
        moderated_at=now,
    )
    modeladmin.message_user(request, f'Одобрено профилей: {updated}.')


@admin.action(description='Отклонить выбранных психологов')
def reject_psychologists(modeladmin, request, queryset):
    now = timezone.now()
    updated = queryset.exclude(moderation_status=PsychologistModerationStatus.REJECTED).update(
        moderation_status=PsychologistModerationStatus.REJECTED,
        moderated_at=now,
    )
    modeladmin.message_user(request, f'Отклонено профилей: {updated}.')


@admin.register(PsychologistProfile)
class PsychologistProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'specialization',
        'license_number',
        'moderation_status',
        'is_accepting_patients',
        'moderated_at',
        'created_at',
    )
    list_filter = ('moderation_status', 'is_accepting_patients')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialization', 'license_number')
    autocomplete_fields = ('user',)
    actions = (approve_psychologists, reject_psychologists)
    readonly_fields = ('moderated_at', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'specialization', 'license_number', 'bio', 'is_accepting_patients'),
        }),
        ('Модерация', {
            'fields': ('moderation_status', 'moderation_note', 'moderated_at'),
        }),
        ('Служебное', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if 'moderation_status' in form.changed_data:
            obj.moderated_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'psychologist', 'date_of_birth', 'created_at')
    list_filter = ('psychologist',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    autocomplete_fields = ('user', 'psychologist')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'psychologist':
            approved_user_ids = PsychologistProfile.objects.filter(
                moderation_status=PsychologistModerationStatus.APPROVED,
            ).values_list('user_id', flat=True)
            kwargs['queryset'] = User.objects.filter(
                role=UserRole.PSYCHOLOGIST,
                pk__in=approved_user_ids,
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
