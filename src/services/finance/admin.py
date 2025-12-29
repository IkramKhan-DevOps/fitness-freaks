from django.contrib import admin
from .models import SubscriptionPlan, Member, Payment, Expense


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration_days', 'price', 'has_personal_trainer', 'has_locker', 'is_active']
    list_filter = ['is_active', 'has_personal_trainer', 'has_locker']
    search_fields = ['name', 'description']
    ordering = ['price']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription_plan', 'subscription_start', 'subscription_end', 'status', 'is_active']
    list_filter = ['status', 'is_active', 'subscription_plan', 'blood_group']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'cnic']
    raw_id_fields = ['user', 'subscription_plan']
    date_hierarchy = 'join_date'
    ordering = ['-created_on']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['member', 'amount', 'payment_method', 'payment_date', 'status', 'received_by']
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = ['member__user__email', 'member__user__first_name', 'reference_number']
    raw_id_fields = ['member', 'subscription_plan', 'received_by']
    date_hierarchy = 'payment_date'
    ordering = ['-payment_date']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'expense_date', 'payment_method', 'added_by']
    list_filter = ['category', 'payment_method', 'is_recurring', 'expense_date']
    search_fields = ['description', 'reference_number']
    raw_id_fields = ['added_by']
    date_hierarchy = 'expense_date'
    ordering = ['-expense_date']

