import django_filters

from .models import SubscriptionPlan, Member, Payment, Expense, SubscriptionStatus, PaymentStatus, PaymentMethodChoice, ExpenseCategory


class SubscriptionPlanFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Plan Name')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Min Price (PKR)')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Max Price (PKR)')
    is_active = django_filters.BooleanFilter(label='Active Only')

    class Meta:
        model = SubscriptionPlan
        fields = ['name', 'is_active', 'has_personal_trainer', 'has_locker']


class MemberFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='Search')
    status = django_filters.ChoiceFilter(choices=SubscriptionStatus.choices)
    subscription_plan = django_filters.ModelChoiceFilter(queryset=SubscriptionPlan.objects.filter(is_active=True))
    expiring_soon = django_filters.BooleanFilter(method='filter_expiring_soon', label='Expiring in 7 days')
    is_active = django_filters.BooleanFilter(label='Active Members')

    class Meta:
        model = Member
        fields = ['status', 'subscription_plan', 'is_active', 'blood_group']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(user__email__icontains=value) |
            models.Q(user__first_name__icontains=value) |
            models.Q(user__last_name__icontains=value) |
            models.Q(cnic__icontains=value) |
            models.Q(emergency_contact_phone__icontains=value)
        )

    def filter_expiring_soon(self, queryset, name, value):
        if value:
            from django.utils import timezone
            from datetime import timedelta
            today = timezone.now().date()
            week_later = today + timedelta(days=7)
            return queryset.filter(
                subscription_end__gte=today,
                subscription_end__lte=week_later,
                status=SubscriptionStatus.ACTIVE
            )
        return queryset


# Need to import models for Q lookups
from django.db import models


class PaymentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='Search')
    status = django_filters.ChoiceFilter(choices=PaymentStatus.choices)
    payment_method = django_filters.ChoiceFilter(choices=PaymentMethodChoice.choices)
    date_from = django_filters.DateFilter(field_name='payment_date', lookup_expr='gte', label='From Date')
    date_to = django_filters.DateFilter(field_name='payment_date', lookup_expr='lte', label='To Date')
    min_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='gte', label='Min Amount')
    max_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='lte', label='Max Amount')

    class Meta:
        model = Payment
        fields = ['status', 'payment_method']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(member__user__email__icontains=value) |
            models.Q(member__user__first_name__icontains=value) |
            models.Q(member__user__last_name__icontains=value) |
            models.Q(reference_number__icontains=value)
        )


class ExpenseFilter(django_filters.FilterSet):
    category = django_filters.ChoiceFilter(choices=ExpenseCategory.choices)
    payment_method = django_filters.ChoiceFilter(choices=PaymentMethodChoice.choices)
    date_from = django_filters.DateFilter(field_name='expense_date', lookup_expr='gte', label='From Date')
    date_to = django_filters.DateFilter(field_name='expense_date', lookup_expr='lte', label='To Date')
    min_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='gte', label='Min Amount')
    max_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='lte', label='Max Amount')
    is_recurring = django_filters.BooleanFilter()

    class Meta:
        model = Expense
        fields = ['category', 'payment_method', 'is_recurring']

