from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

from src.core.bll import get_action_urls


class PaymentMethodChoice(models.TextChoices):
    CASH = 'cash', 'Cash'
    JAZZCASH = 'jazzcash', 'JazzCash'
    EASYPAISA = 'easypaisa', 'Easypaisa'
    BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
    CARD = 'card', 'Debit/Credit Card'


class SubscriptionStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    EXPIRED = 'expired', 'Expired'
    CANCELLED = 'cancelled', 'Cancelled'
    PENDING = 'pending', 'Pending Payment'


class PaymentStatus(models.TextChoices):
    PAID = 'paid', 'Paid'
    PENDING = 'pending', 'Pending'
    FAILED = 'failed', 'Failed'
    REFUNDED = 'refunded', 'Refunded'


class ExpenseCategory(models.TextChoices):
    RENT = 'rent', 'Rent'
    UTILITIES = 'utilities', 'Utilities (Electricity/Gas/Water)'
    SALARIES = 'salaries', 'Staff Salaries'
    EQUIPMENT = 'equipment', 'Equipment Purchase'
    MAINTENANCE = 'maintenance', 'Maintenance & Repairs'
    MARKETING = 'marketing', 'Marketing & Advertising'
    SUPPLIES = 'supplies', 'Gym Supplies (Towels, Sanitizer, etc.)'
    OTHER = 'other', 'Other'


""" SUBSCRIPTION PLAN """


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    duration_days = models.PositiveIntegerField(
        help_text='Duration in days (e.g., 30 for monthly, 365 for yearly)'
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Price in PKR'
    )
    description = models.TextField(blank=True, null=True)

    # Features
    has_personal_trainer = models.BooleanField(default=False)
    has_locker = models.BooleanField(default=False)
    has_cardio_access = models.BooleanField(default=True)
    has_weight_training = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    allowed_actions = ['delete', 'update']

    class Meta:
        ordering = ['price']
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'

    def __str__(self):
        return f"{self.name} - {self.duration_days} days - PKR {self.price}"

    def get_display_fields(self):
        return ['name', 'duration_days', 'price', 'has_personal_trainer', 'has_locker', 'is_active']

    def get_action_urls(self, user):
        return get_action_urls(self, user, True)


""" MEMBER """


class Member(models.Model):
    user = models.OneToOneField(
        'accounts.User', on_delete=models.CASCADE, related_name='member_profile'
    )
    subscription_plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='members'
    )

    # Pakistan-specific fields
    cnic = models.CharField(
        max_length=15, blank=True, null=True, unique=True,
        help_text='CNIC Number (e.g., 12345-1234567-1)'
    )
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)

    # Health Information
    blood_group = models.CharField(
        max_length=5, blank=True, null=True,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ]
    )
    health_conditions = models.TextField(
        blank=True, null=True,
        help_text='Any medical conditions, allergies, or health concerns'
    )
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        help_text='Weight in KG'
    )
    height = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        help_text='Height in CM'
    )

    # Subscription Details
    subscription_start = models.DateField(null=True, blank=True)
    subscription_end = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=SubscriptionStatus.choices, default=SubscriptionStatus.PENDING
    )

    # Metadata
    join_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    allowed_actions = ['delete', 'update', 'detail']

    class Meta:
        ordering = ['-created_on']
        verbose_name = 'Member'
        verbose_name_plural = 'Members'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email}"

    def get_display_fields(self):
        return ['user', 'subscription_plan', 'subscription_start', 'subscription_end', 'status', 'is_active']

    def get_action_urls(self, user):
        return get_action_urls(self, user, True)

    @property
    def is_subscription_active(self):
        if self.subscription_end and self.subscription_end >= timezone.now().date():
            return True
        return False

    @property
    def days_remaining(self):
        if self.subscription_end:
            remaining = (self.subscription_end - timezone.now().date()).days
            return max(0, remaining)
        return 0

    def update_status(self):
        """Update member status based on subscription end date"""
        if self.subscription_end:
            if self.subscription_end < timezone.now().date():
                self.status = SubscriptionStatus.EXPIRED
            elif self.status == SubscriptionStatus.EXPIRED:
                self.status = SubscriptionStatus.ACTIVE
        self.save()


""" PAYMENT """


class Payment(models.Model):
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='payments'
    )
    subscription_plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True
    )

    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Amount in PKR'
    )
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Discount in PKR'
    )

    payment_method = models.CharField(
        max_length=20, choices=PaymentMethodChoice.choices, default=PaymentMethodChoice.CASH
    )
    payment_date = models.DateTimeField(default=timezone.now)
    reference_number = models.CharField(
        max_length=100, blank=True, null=True,
        help_text='Transaction ID / Receipt Number'
    )

    status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PAID
    )
    notes = models.TextField(blank=True, null=True)

    # Subscription period this payment covers
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)

    received_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='received_payments'
    )

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    allowed_actions = ['delete', 'update', 'detail']

    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"{self.member} - PKR {self.amount} - {self.payment_date.strftime('%Y-%m-%d')}"

    def get_display_fields(self):
        return ['member', 'amount', 'payment_method', 'payment_date', 'status']

    def get_action_urls(self, user):
        return get_action_urls(self, user, True)

    @property
    def net_amount(self):
        return self.amount - self.discount

    def save(self, *args, **kwargs):
        # Auto-update member subscription on successful payment
        if self.status == PaymentStatus.PAID and self.subscription_plan:
            member = self.member
            if not self.period_start:
                self.period_start = timezone.now().date()
            if not self.period_end:
                from datetime import timedelta
                self.period_end = self.period_start + timedelta(days=self.subscription_plan.duration_days)

            # Update member subscription dates
            if not member.subscription_start or self.period_start < member.subscription_start:
                member.subscription_start = self.period_start
            if not member.subscription_end or self.period_end > member.subscription_end:
                member.subscription_end = self.period_end
            member.subscription_plan = self.subscription_plan
            member.status = SubscriptionStatus.ACTIVE
            member.save()

        super().save(*args, **kwargs)


""" EXPENSE """


class Expense(models.Model):
    category = models.CharField(
        max_length=20, choices=ExpenseCategory.choices, default=ExpenseCategory.OTHER
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Amount in PKR'
    )
    description = models.TextField()
    expense_date = models.DateField(default=timezone.now)

    payment_method = models.CharField(
        max_length=20, choices=PaymentMethodChoice.choices, default=PaymentMethodChoice.CASH
    )
    reference_number = models.CharField(
        max_length=100, blank=True, null=True,
        help_text='Receipt/Invoice Number'
    )

    added_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='added_expenses'
    )

    is_recurring = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    allowed_actions = ['delete', 'update']

    class Meta:
        ordering = ['-expense_date']
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'

    def __str__(self):
        return f"{self.get_category_display()} - PKR {self.amount} - {self.expense_date}"

    def get_display_fields(self):
        return ['category', 'amount', 'expense_date', 'payment_method', 'added_by']

    def get_action_urls(self, user):
        return get_action_urls(self, user, True)

