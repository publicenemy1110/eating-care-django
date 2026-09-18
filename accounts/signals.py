from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PatientProfile, PsychologistModerationStatus, PsychologistProfile, User, UserRole


@receiver(post_save, sender=User)
def create_role_profile(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.role == UserRole.PSYCHOLOGIST:
        PsychologistProfile.objects.get_or_create(
            user=instance,
            defaults={
                'moderation_status': PsychologistModerationStatus.PENDING,
                'moderation_note': '',
            },
        )
    elif instance.role == UserRole.PATIENT:
        PatientProfile.objects.get_or_create(user=instance)
