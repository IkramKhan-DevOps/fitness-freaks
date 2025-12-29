#!/usr/bin/env python
"""
Faker Script for Fitness Freaks Gym Management App
Generates fake data for: Accounts, Whisper, and Finance apps

Usage:
    python docs/bash/generate_fake_data.py

Or via shell script:
    bash docs/bash/faker.sh

Options:
    --clear    Delete existing data before generating new data
"""

import os
import sys
import django
import random
from datetime import timedelta
from decimal import Decimal

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')
django.setup()

from faker import Faker
from django.utils import timezone
from django.contrib.auth import get_user_model

# Import models
from src.services.accounts.models import UserType
from src.services.finance.models import (
    SubscriptionPlan, Member, Payment, Expense,
    PaymentMethodChoice, SubscriptionStatus, PaymentStatus, ExpenseCategory
)
from src.apps.whisper.models import EmailNotification

# Initialize Faker with Pakistani locale
fake = Faker(['en_PK', 'en_US'])
User = get_user_model()


def generate_pakistani_phone():
    """Generate Pakistani phone number format (0XX) XXX-XXXX"""
    prefixes = ['300', '301', '302', '303', '304', '305', '306', '307', '308', '309',
                '310', '311', '312', '313', '314', '315', '316', '317', '318', '319',
                '320', '321', '322', '323', '324', '325', '331', '332', '333', '334']
    prefix = random.choice(prefixes)
    number = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return f"(0{prefix[0]}{prefix[1]}) {prefix[2]}{number[:2]}-{number[2:]}"


def generate_cnic():
    """Generate Pakistani CNIC number format: XXXXX-XXXXXXX-X"""
    part1 = ''.join([str(random.randint(0, 9)) for _ in range(5)])
    part2 = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    part3 = str(random.randint(0, 9))
    return f"{part1}-{part2}-{part3}"


def create_users(count=20):
    """Create fake users"""
    print(f"\n📧 Creating {count} users...")
    users = []

    for i in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{fake.free_email_domain()}"

        # Ensure unique email
        while User.objects.filter(email=email).exists():
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 9999)}@{fake.free_email_domain()}"

        user_type = random.choices(
            [UserType.client, UserType.administration],
            weights=[90, 10]
        )[0]

        user = User.objects.create_user(
            username=email.split('@')[0] + str(random.randint(1, 9999)),
            email=email,
            password='password123',
            first_name=first_name,
            last_name=last_name,
            phone_number=generate_pakistani_phone(),
            user_type=user_type,
            is_active=True,
            is_staff=user_type == UserType.administration,
        )
        users.append(user)

        if (i + 1) % 10 == 0:
            print(f"   Created {i + 1} users...")

    print(f"   ✅ Created {len(users)} users")
    return users


def create_subscription_plans():
    """Create subscription plans"""
    print("\n💳 Creating subscription plans...")

    plans_data = [
        {
            'name': 'Daily Pass',
            'duration_days': 1,
            'price': Decimal('500.00'),
            'description': 'Single day access to gym facilities',
            'has_personal_trainer': False,
            'has_locker': False,
        },
        {
            'name': 'Weekly Basic',
            'duration_days': 7,
            'price': Decimal('2000.00'),
            'description': 'One week access to cardio and weight training',
            'has_personal_trainer': False,
            'has_locker': False,
        },
        {
            'name': 'Monthly Basic',
            'duration_days': 30,
            'price': Decimal('5000.00'),
            'description': 'Monthly access to all gym equipment',
            'has_personal_trainer': False,
            'has_locker': False,
        },
        {
            'name': 'Monthly Premium',
            'duration_days': 30,
            'price': Decimal('8000.00'),
            'description': 'Monthly access with locker and personal trainer sessions',
            'has_personal_trainer': True,
            'has_locker': True,
        },
        {
            'name': 'Quarterly Basic',
            'duration_days': 90,
            'price': Decimal('12000.00'),
            'description': '3 months access - Save PKR 3000!',
            'has_personal_trainer': False,
            'has_locker': True,
        },
        {
            'name': 'Quarterly Premium',
            'duration_days': 90,
            'price': Decimal('20000.00'),
            'description': '3 months with personal trainer and all amenities',
            'has_personal_trainer': True,
            'has_locker': True,
        },
        {
            'name': 'Half Yearly',
            'duration_days': 180,
            'price': Decimal('25000.00'),
            'description': '6 months access - Best value!',
            'has_personal_trainer': False,
            'has_locker': True,
        },
        {
            'name': 'Annual Membership',
            'duration_days': 365,
            'price': Decimal('45000.00'),
            'description': 'Full year access with all benefits included',
            'has_personal_trainer': True,
            'has_locker': True,
        },
        {
            'name': 'Student Monthly',
            'duration_days': 30,
            'price': Decimal('3500.00'),
            'description': 'Discounted monthly plan for students (ID required)',
            'has_personal_trainer': False,
            'has_locker': False,
        },
        {
            'name': 'Couple Monthly',
            'duration_days': 30,
            'price': Decimal('9000.00'),
            'description': 'Monthly plan for couples - train together!',
            'has_personal_trainer': False,
            'has_locker': True,
        },
    ]

    plans = []
    for plan_data in plans_data:
        plan, created = SubscriptionPlan.objects.get_or_create(
            name=plan_data['name'],
            defaults=plan_data
        )
        plans.append(plan)
        status = "Created" if created else "Already exists"
        print(f"   {status}: {plan.name} - PKR {plan.price}")

    print(f"   ✅ {len(plans)} subscription plans ready")
    return plans


def create_members(users, plans, count=50):
    """Create fake gym members"""
    print(f"\n🏋️ Creating {count} gym members...")

    members = []
    available_users = [u for u in users if not hasattr(u, 'member_profile')]

    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    health_conditions = [
        None, None, None,  # Most people have no conditions
        'Mild asthma - uses inhaler',
        'Previous knee injury - avoid heavy leg exercises',
        'Diabetic - Type 2',
        'High blood pressure - on medication',
        'Lower back pain',
        'Recovering from shoulder surgery',
        None, None
    ]

    for i in range(min(count, len(available_users))):
        user = available_users[i]
        plan = random.choice(plans)

        # Random join date in last 6 months
        join_date = timezone.now().date() - timedelta(days=random.randint(0, 180))

        # Subscription dates
        sub_start = join_date
        sub_end = sub_start + timedelta(days=plan.duration_days)

        # Determine status based on dates
        today = timezone.now().date()
        if sub_end < today:
            status = SubscriptionStatus.EXPIRED
        elif random.random() < 0.1:  # 10% pending
            status = SubscriptionStatus.PENDING
        else:
            status = SubscriptionStatus.ACTIVE
            # Adjust end date for active members
            sub_end = today + timedelta(days=random.randint(1, plan.duration_days))

        member = Member.objects.create(
            user=user,
            subscription_plan=plan,
            cnic=generate_cnic(),
            emergency_contact_name=fake.name(),
            emergency_contact_phone=generate_pakistani_phone(),
            blood_group=random.choice(blood_groups),
            health_conditions=random.choice(health_conditions),
            weight=Decimal(str(round(random.uniform(50, 120), 1))),
            height=Decimal(str(round(random.uniform(150, 195), 1))),
            subscription_start=sub_start,
            subscription_end=sub_end,
            status=status,
            join_date=join_date,
            notes=fake.sentence() if random.random() < 0.3 else None,
            is_active=True
        )
        members.append(member)

        if (i + 1) % 10 == 0:
            print(f"   Created {i + 1} members...")

    print(f"   ✅ Created {len(members)} members")
    return members


def create_payments(members, staff_users, count=100):
    """Create fake payments"""
    print(f"\n💰 Creating {count} payments...")

    payments = []
    payment_methods = list(PaymentMethodChoice.values)

    for i in range(count):
        member = random.choice(members)
        plan = member.subscription_plan or random.choice(SubscriptionPlan.objects.all())

        # Random payment date in last 6 months
        payment_date = timezone.now() - timedelta(
            days=random.randint(0, 180),
            hours=random.randint(8, 20),
            minutes=random.randint(0, 59)
        )

        # Most payments are successful
        status = random.choices(
            [PaymentStatus.PAID, PaymentStatus.PENDING, PaymentStatus.FAILED],
            weights=[85, 10, 5]
        )[0]

        # Discount for some payments
        discount = Decimal('0.00')
        if random.random() < 0.2:  # 20% get discount
            discount = Decimal(str(random.choice([500, 1000, 1500, 2000])))

        period_start = payment_date.date()
        period_end = period_start + timedelta(days=plan.duration_days)

        # Generate reference number for non-cash payments
        payment_method = random.choice(payment_methods)
        reference = None
        if payment_method != PaymentMethodChoice.CASH:
            reference = ''.join([str(random.randint(0, 9)) for _ in range(12)])

        payment = Payment.objects.create(
            member=member,
            subscription_plan=plan,
            amount=plan.price,
            discount=discount,
            payment_method=payment_method,
            payment_date=payment_date,
            reference_number=reference,
            status=status,
            period_start=period_start,
            period_end=period_end,
            received_by=random.choice(staff_users) if staff_users else None,
            notes=fake.sentence() if random.random() < 0.1 else None
        )
        payments.append(payment)

        if (i + 1) % 25 == 0:
            print(f"   Created {i + 1} payments...")

    print(f"   ✅ Created {len(payments)} payments")
    return payments


def create_expenses(staff_users, count=50):
    """Create fake expenses"""
    print(f"\n📊 Creating {count} expenses...")

    expenses = []
    categories = list(ExpenseCategory.values)
    payment_methods = list(PaymentMethodChoice.values)

    expense_descriptions = {
        ExpenseCategory.RENT: [
            'Monthly gym space rent',
            'Rent for December 2024',
            'Building rent payment',
        ],
        ExpenseCategory.UTILITIES: [
            'Electricity bill - December',
            'Water bill payment',
            'Gas bill for heating',
            'Internet and WiFi charges',
        ],
        ExpenseCategory.SALARIES: [
            'Staff salaries - Month end',
            'Trainer salary payment',
            'Receptionist salary',
            'Cleaning staff wages',
        ],
        ExpenseCategory.EQUIPMENT: [
            'New treadmill purchase',
            'Dumbbells set (5-50 kg)',
            'Yoga mats (pack of 20)',
            'Resistance bands',
            'Bench press equipment',
        ],
        ExpenseCategory.MAINTENANCE: [
            'AC repair and servicing',
            'Treadmill belt replacement',
            'Plumbing repair',
            'Electrical maintenance',
        ],
        ExpenseCategory.MARKETING: [
            'Facebook ads campaign',
            'Flyer printing (1000 pcs)',
            'Banner and standee',
            'Instagram promotion',
        ],
        ExpenseCategory.SUPPLIES: [
            'Towels purchase (50 pcs)',
            'Hand sanitizers (bulk)',
            'Cleaning supplies',
            'Paper towels and tissues',
            'Water dispenser refill',
        ],
        ExpenseCategory.OTHER: [
            'Miscellaneous expenses',
            'Office supplies',
            'First aid kit refill',
            'Fire extinguisher service',
        ],
    }

    amount_ranges = {
        ExpenseCategory.RENT: (50000, 150000),
        ExpenseCategory.UTILITIES: (10000, 50000),
        ExpenseCategory.SALARIES: (20000, 80000),
        ExpenseCategory.EQUIPMENT: (5000, 200000),
        ExpenseCategory.MAINTENANCE: (2000, 30000),
        ExpenseCategory.MARKETING: (5000, 50000),
        ExpenseCategory.SUPPLIES: (1000, 15000),
        ExpenseCategory.OTHER: (500, 10000),
    }

    for i in range(count):
        category = random.choice(categories)

        # Random expense date in last 6 months
        expense_date = timezone.now().date() - timedelta(days=random.randint(0, 180))

        min_amt, max_amt = amount_ranges.get(category, (1000, 10000))
        amount = Decimal(str(random.randint(min_amt, max_amt)))

        description = random.choice(expense_descriptions.get(category, ['General expense']))

        expense = Expense.objects.create(
            category=category,
            amount=amount,
            description=description,
            expense_date=expense_date,
            payment_method=random.choice(payment_methods),
            reference_number=''.join([str(random.randint(0, 9)) for _ in range(8)]) if random.random() < 0.5 else None,
            added_by=random.choice(staff_users) if staff_users else None,
            is_recurring=category in [ExpenseCategory.RENT, ExpenseCategory.UTILITIES, ExpenseCategory.SALARIES]
        )
        expenses.append(expense)

        if (i + 1) % 10 == 0:
            print(f"   Created {i + 1} expenses...")

    print(f"   ✅ Created {len(expenses)} expenses")
    return expenses


def create_email_notifications(users, count=30):
    """Create fake email notifications"""
    print(f"\n📧 Creating {count} email notifications...")

    notifications = []
    statuses = ['pending', 'sent', 'failed', 'retry']

    subjects = [
        'Welcome to Fitness Freaks Gym!',
        'Your subscription is expiring soon',
        'Payment received - Thank you!',
        'Renew your membership today',
        'New offers available for you',
        'Your workout summary',
        'Gym schedule update',
        'Password reset request',
        'Account verification',
        'Monthly newsletter',
    ]

    templates = [
        'welcome_email',
        'subscription_expiry',
        'payment_confirmation',
        'renewal_reminder',
        'promotional_offer',
        'workout_summary',
        'schedule_update',
        'password_reset',
        'verification',
        'newsletter',
    ]

    for i in range(count):
        user = random.choice(users)
        subject_idx = random.randint(0, len(subjects) - 1)

        status = random.choices(
            statuses,
            weights=[10, 70, 15, 5]
        )[0]

        created_at = timezone.now() - timedelta(
            days=random.randint(0, 60),
            hours=random.randint(0, 23)
        )

        notification = EmailNotification.objects.create(
            subject=subjects[subject_idx],
            body=fake.paragraph(nb_sentences=5),
            recipient=user.email,
            status=status,
            failed_attempts=random.randint(0, 3) if status in ['failed', 'retry'] else 0,
            template_name=templates[subject_idx],
            error_message='SMTP connection timeout' if status == 'failed' else None,
        )
        notifications.append(notification)

        if (i + 1) % 10 == 0:
            print(f"   Created {i + 1} notifications...")

    print(f"   ✅ Created {len(notifications)} email notifications")
    return notifications


def main():
    """Main function to generate all fake data"""
    print("=" * 60)
    print("🏋️ FITNESS FREAKS - FAKE DATA GENERATOR")
    print("=" * 60)

    # Check if we should clear existing data
    if '--clear' in sys.argv:
        print("\n⚠️  Clearing existing data...")
        Payment.objects.all().delete()
        Expense.objects.all().delete()
        Member.objects.all().delete()
        EmailNotification.objects.all().delete()
        # Don't delete SubscriptionPlans - they're standard
        User.objects.filter(is_superuser=False).delete()
        print("   ✅ Data cleared")

    # Create subscription plans first (they're standard)
    plans = create_subscription_plans()

    # Create users
    users = create_users(count=30)

    # Get staff users for assignments
    staff_users = list(User.objects.filter(is_staff=True))

    # Create members from users
    members = create_members(users, plans, count=25)

    # Create payments
    create_payments(members, staff_users, count=80)

    # Create expenses
    create_expenses(staff_users, count=40)

    # Create email notifications
    create_email_notifications(users, count=25)

    # Summary
    print("\n" + "=" * 60)
    print("✅ FAKE DATA GENERATION COMPLETE!")
    print("=" * 60)
    print(f"""
📊 Summary:
   • Users: {User.objects.count()}
   • Subscription Plans: {SubscriptionPlan.objects.count()}
   • Members: {Member.objects.count()}
   • Payments: {Payment.objects.count()}
   • Expenses: {Expense.objects.count()}
   • Email Notifications: {EmailNotification.objects.count()}
   
💡 Default password for all users: password123
   
🌐 Access the dashboard at: http://127.0.0.1:8000/dashboard/
""")


if __name__ == '__main__':
    main()

