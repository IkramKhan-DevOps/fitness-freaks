from django import forms
from django.utils import timezone
from datetime import timedelta

from .models import SubscriptionPlan, Member, Payment, Expense


class SubscriptionPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'name', 'duration_days', 'price', 'description',
            'has_personal_trainer', 'has_locker', 'has_cardio_access', 'has_weight_training',
            'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'user', 'subscription_plan',
            'cnic', 'emergency_contact_name', 'emergency_contact_phone',
            'blood_group', 'health_conditions', 'weight', 'height',
            'subscription_start', 'subscription_end', 'status',
            'join_date', 'notes', 'is_active'
        ]
        widgets = {
            'health_conditions': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'subscription_start': forms.DateInput(attrs={'type': 'date'}),
            'subscription_end': forms.DateInput(attrs={'type': 'date'}),
            'join_date': forms.DateInput(attrs={'type': 'date'}),
        }


class MemberQuickAddForm(forms.ModelForm):
    """Simplified form for quick member registration"""
    class Meta:
        model = Member
        fields = [
            'user', 'subscription_plan', 'cnic',
            'emergency_contact_name', 'emergency_contact_phone',
            'blood_group', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'member', 'subscription_plan', 'amount', 'discount',
            'payment_method', 'payment_date', 'reference_number',
            'status', 'period_start', 'period_end', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'payment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Auto-populate amount when subscription plan changes
        if 'subscription_plan' in self.data:
            try:
                plan_id = int(self.data.get('subscription_plan'))
                plan = SubscriptionPlan.objects.get(pk=plan_id)
                self.fields['amount'].initial = plan.price
            except (ValueError, SubscriptionPlan.DoesNotExist):
                pass


class QuickPaymentForm(forms.ModelForm):
    """Simplified payment form for quick fee collection"""
    class Meta:
        model = Payment
        fields = ['member', 'subscription_plan', 'amount', 'discount', 'payment_method', 'reference_number', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.subscription_plan:
            instance.period_start = timezone.now().date()
            instance.period_end = instance.period_start + timedelta(days=instance.subscription_plan.duration_days)
        if commit:
            instance.save()
        return instance


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'category', 'amount', 'description', 'expense_date',
            'payment_method', 'reference_number', 'is_recurring'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'expense_date': forms.DateInput(attrs={'type': 'date'}),
        }


class RenewSubscriptionForm(forms.Form):
    """Form for renewing member subscription"""
    subscription_plan = forms.ModelChoiceField(
        queryset=SubscriptionPlan.objects.filter(is_active=True),
        label='Subscription Plan'
    )
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label='Amount (PKR)')
    discount = forms.DecimalField(
        max_digits=10, decimal_places=2, initial=0, required=False, label='Discount (PKR)'
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('cash', 'Cash'),
            ('jazzcash', 'JazzCash'),
            ('easypaisa', 'Easypaisa'),
            ('bank_transfer', 'Bank Transfer'),
            ('card', 'Debit/Credit Card'),
        ],
        initial='cash'
    )
    reference_number = forms.CharField(max_length=100, required=False, label='Reference/Receipt No.')
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)

