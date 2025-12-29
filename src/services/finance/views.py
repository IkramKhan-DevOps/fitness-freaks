from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView
from datetime import timedelta

from .filters import SubscriptionPlanFilter, MemberFilter, PaymentFilter, ExpenseFilter
from .forms import SubscriptionPlanForm, MemberForm, PaymentForm, ExpenseForm, RenewSubscriptionForm
from .mixins import FinanceListViewMixin, FinanceDetailViewMixin, FinanceDeleteViewMixin
from .models import SubscriptionPlan, Member, Payment, Expense, SubscriptionStatus, PaymentStatus
from src.core.views import AjaxCRUDView


""" SUBSCRIPTION PLAN VIEWS """


class SubscriptionPlanListView(FinanceListViewMixin):
    model = SubscriptionPlan
    filter_class = SubscriptionPlanFilter


class SubscriptionPlanCreateView(AjaxCRUDView):
    model = SubscriptionPlan
    form_class = SubscriptionPlanForm


class SubscriptionPlanUpdateView(AjaxCRUDView):
    model = SubscriptionPlan
    form_class = SubscriptionPlanForm


class SubscriptionPlanDeleteView(FinanceDeleteViewMixin):
    model = SubscriptionPlan
    redirect_url = 'finance:subscriptionplan_list'


""" MEMBER VIEWS """


class MemberListView(FinanceListViewMixin):
    model = Member
    filter_class = MemberFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        # Update expired statuses
        today = timezone.now().date()
        queryset.filter(
            subscription_end__lt=today,
            status=SubscriptionStatus.ACTIVE
        ).update(status=SubscriptionStatus.EXPIRED)
        return queryset


class MemberDetailView(FinanceDetailViewMixin, DetailView):
    model = Member
    template_name = 'finance/member_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = self.object.payments.all()[:10]
        context['renew_form'] = RenewSubscriptionForm(
            initial={'subscription_plan': self.object.subscription_plan}
        )
        return context


class MemberCreateView(AjaxCRUDView):
    model = Member
    form_class = MemberForm


class MemberUpdateView(AjaxCRUDView):
    model = Member
    form_class = MemberForm


class MemberDeleteView(FinanceDeleteViewMixin):
    model = Member
    redirect_url = 'finance:member_list'


""" PAYMENT VIEWS """


class PaymentListView(FinanceListViewMixin):
    model = Payment
    filter_class = PaymentFilter


class PaymentDetailView(FinanceDetailViewMixin, DetailView):
    model = Payment
    template_name = 'finance/payment_detail.html'


class PaymentCreateView(AjaxCRUDView):
    model = Payment
    form_class = PaymentForm

    def post_additional_data(self, instance):
        instance.received_by = self.request.user


class PaymentUpdateView(AjaxCRUDView):
    model = Payment
    form_class = PaymentForm


class PaymentDeleteView(FinanceDeleteViewMixin):
    model = Payment
    redirect_url = 'finance:payment_list'


""" EXPENSE VIEWS """


class ExpenseListView(FinanceListViewMixin):
    model = Expense
    filter_class = ExpenseFilter


class ExpenseCreateView(AjaxCRUDView):
    model = Expense
    form_class = ExpenseForm

    def post_additional_data(self, instance):
        instance.added_by = self.request.user


class ExpenseUpdateView(AjaxCRUDView):
    model = Expense
    form_class = ExpenseForm


class ExpenseDeleteView(FinanceDeleteViewMixin):
    model = Expense
    redirect_url = 'finance:expense_list'


""" QUICK ACTIONS """


class RenewMemberSubscriptionView(AjaxCRUDView):
    """Quick action to renew a member's subscription"""
    model = Payment

    def post(self, request, *args, **kwargs):
        member = get_object_or_404(Member, pk=kwargs.get('pk'))
        form = RenewSubscriptionForm(request.POST)

        if form.is_valid():
            plan = form.cleaned_data['subscription_plan']

            # Calculate new subscription period
            today = timezone.now().date()
            if member.subscription_end and member.subscription_end > today:
                # Extend from current end date
                period_start = member.subscription_end
            else:
                period_start = today
            period_end = period_start + timedelta(days=plan.duration_days)

            # Create payment
            payment = Payment.objects.create(
                member=member,
                subscription_plan=plan,
                amount=form.cleaned_data['amount'],
                discount=form.cleaned_data.get('discount') or 0,
                payment_method=form.cleaned_data['payment_method'],
                reference_number=form.cleaned_data.get('reference_number'),
                notes=form.cleaned_data.get('notes'),
                period_start=period_start,
                period_end=period_end,
                status=PaymentStatus.PAID,
                received_by=request.user
            )

            messages.success(request, f'Subscription renewed successfully until {period_end}')
            return redirect('finance:member_detail', pk=member.pk)

        messages.error(request, 'Failed to renew subscription. Please check the form.')
        return redirect('finance:member_detail', pk=member.pk)

