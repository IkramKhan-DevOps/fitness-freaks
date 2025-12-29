from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Payment, Member, SubscriptionStatus, PaymentStatus


@receiver(post_save, sender=Payment)
def update_member_on_payment(sender, instance, created, **kwargs):
    """
    Update member subscription status when a payment is made.
    """
    if instance.status == PaymentStatus.PAID and instance.member:
        member = instance.member
        if instance.period_end:
            if not member.subscription_end or instance.period_end > member.subscription_end:
                member.subscription_end = instance.period_end
            if instance.period_start and (not member.subscription_start or instance.period_start < member.subscription_start):
                member.subscription_start = instance.period_start
            member.status = SubscriptionStatus.ACTIVE
            if instance.subscription_plan:
                member.subscription_plan = instance.subscription_plan
            member.save(update_fields=['subscription_start', 'subscription_end', 'status', 'subscription_plan'])

