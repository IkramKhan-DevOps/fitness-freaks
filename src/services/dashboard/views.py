from django.utils.decorators import method_decorator
from django.views.generic import (
    TemplateView
)
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from datetime import timedelta
from decimal import Decimal

from src.services.accounts.decorators import staff_required_decorator


def get_dashboard_statistics():
    """Calculate all dashboard statistics"""
    from src.services.finance.models import Member, Payment, Expense, SubscriptionPlan, SubscriptionStatus, PaymentStatus

    today = timezone.now().date()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    week_later = today + timedelta(days=7)

    stats = {}

    # Member Statistics
    stats['total_members'] = Member.objects.filter(is_active=True).count()
    stats['active_members'] = Member.objects.filter(status=SubscriptionStatus.ACTIVE, is_active=True).count()
    stats['expired_members'] = Member.objects.filter(status=SubscriptionStatus.EXPIRED, is_active=True).count()
    stats['pending_members'] = Member.objects.filter(status=SubscriptionStatus.PENDING, is_active=True).count()
    stats['new_members_today'] = Member.objects.filter(join_date=today).count()
    stats['new_members_month'] = Member.objects.filter(join_date__gte=month_start).count()

    # Expiring Soon (next 7 days)
    stats['expiring_soon'] = Member.objects.filter(
        subscription_end__gte=today,
        subscription_end__lte=week_later,
        status=SubscriptionStatus.ACTIVE
    ).count()
    stats['expiring_members'] = Member.objects.filter(
        subscription_end__gte=today,
        subscription_end__lte=week_later,
        status=SubscriptionStatus.ACTIVE
    ).select_related('user', 'subscription_plan')[:5]

    # Revenue Statistics (Payments)
    paid_payments = Payment.objects.filter(status=PaymentStatus.PAID)

    stats['revenue_today'] = paid_payments.filter(
        payment_date__date=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    stats['revenue_month'] = paid_payments.filter(
        payment_date__date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    stats['revenue_year'] = paid_payments.filter(
        payment_date__date__gte=year_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    stats['payments_today'] = paid_payments.filter(payment_date__date=today).count()
    stats['payments_month'] = paid_payments.filter(payment_date__date__gte=month_start).count()

    # Expense Statistics
    stats['expenses_today'] = Expense.objects.filter(
        expense_date=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    stats['expenses_month'] = Expense.objects.filter(
        expense_date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    stats['expenses_year'] = Expense.objects.filter(
        expense_date__gte=year_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Net Profit
    stats['net_profit_month'] = stats['revenue_month'] - stats['expenses_month']
    stats['net_profit_year'] = stats['revenue_year'] - stats['expenses_year']

    # Recent Payments
    stats['recent_payments'] = Payment.objects.filter(
        status=PaymentStatus.PAID
    ).select_related('member__user', 'subscription_plan').order_by('-payment_date')[:5]

    # Subscription Plan Distribution
    stats['plan_distribution'] = SubscriptionPlan.objects.filter(is_active=True).annotate(
        member_count=Count('members', filter=Q(members__status=SubscriptionStatus.ACTIVE))
    ).values('name', 'member_count').order_by('-member_count')

    # Monthly Revenue Chart Data (last 6 months)
    six_months_ago = today - timedelta(days=180)
    monthly_revenue = paid_payments.filter(
        payment_date__date__gte=six_months_ago
    ).annotate(
        month=TruncMonth('payment_date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    stats['chart_labels'] = [item['month'].strftime('%b %Y') for item in monthly_revenue]
    stats['chart_revenue'] = [float(item['total']) for item in monthly_revenue]

    # Monthly Expenses Chart Data
    monthly_expenses = Expense.objects.filter(
        expense_date__gte=six_months_ago
    ).annotate(
        month=TruncMonth('expense_date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    stats['chart_expenses'] = [float(item['total']) for item in monthly_expenses]

    # Payment Method Distribution
    stats['payment_methods'] = paid_payments.filter(
        payment_date__date__gte=month_start
    ).values('payment_method').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-total')

    return stats


@method_decorator(staff_required_decorator, name='dispatch')
class DashboardView(TemplateView):
    """
    Gym Dashboard with comprehensive statistics
    - Member stats: Total, Active, Expired, Expiring Soon
    - Revenue: Today, Month, Year with charts
    - Expenses tracking and comparison
    - Recent activity feed
    """
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context.update(get_dashboard_statistics())
        return context



