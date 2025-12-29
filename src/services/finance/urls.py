from django.urls import path
from .views import (
    SubscriptionPlanListView, SubscriptionPlanCreateView, SubscriptionPlanUpdateView, SubscriptionPlanDeleteView,
    MemberListView, MemberDetailView, MemberCreateView, MemberUpdateView, MemberDeleteView,
    PaymentListView, PaymentDetailView, PaymentCreateView, PaymentUpdateView, PaymentDeleteView,
    ExpenseListView, ExpenseCreateView, ExpenseUpdateView, ExpenseDeleteView,
    RenewMemberSubscriptionView,
)

app_name = 'finance'
urlpatterns = [
    # Subscription Plans
    path('plans/', SubscriptionPlanListView.as_view(), name='subscriptionplan_list'),
    path('plans/create/', SubscriptionPlanCreateView.as_view(), name='subscriptionplan_create'),
    path('plans/update/<int:pk>/', SubscriptionPlanUpdateView.as_view(), name='subscriptionplan_update'),
    path('plans/delete/<int:pk>/', SubscriptionPlanDeleteView.as_view(), name='subscriptionplan_delete'),

    # Members
    path('members/', MemberListView.as_view(), name='member_list'),
    path('members/<int:pk>/', MemberDetailView.as_view(), name='member_detail'),
    path('members/create/', MemberCreateView.as_view(), name='member_create'),
    path('members/update/<int:pk>/', MemberUpdateView.as_view(), name='member_update'),
    path('members/delete/<int:pk>/', MemberDeleteView.as_view(), name='member_delete'),
    path('members/<int:pk>/renew/', RenewMemberSubscriptionView.as_view(), name='member_renew'),

    # Payments
    path('payments/', PaymentListView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment_detail'),
    path('payments/create/', PaymentCreateView.as_view(), name='payment_create'),
    path('payments/update/<int:pk>/', PaymentUpdateView.as_view(), name='payment_update'),
    path('payments/delete/<int:pk>/', PaymentDeleteView.as_view(), name='payment_delete'),

    # Expenses
    path('expenses/', ExpenseListView.as_view(), name='expense_list'),
    path('expenses/create/', ExpenseCreateView.as_view(), name='expense_create'),
    path('expenses/update/<int:pk>/', ExpenseUpdateView.as_view(), name='expense_update'),
    path('expenses/delete/<int:pk>/', ExpenseDeleteView.as_view(), name='expense_delete'),
]
