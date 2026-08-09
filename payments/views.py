from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from core.utils import log_activity
from payments.models import CreditPackage, Transaction

DEFAULT_PACKAGES = [
    {'name': 'Starter Pack', 'credits': 100, 'price': Decimal('9.00'), 'is_popular': False},
    {'name': 'Creator Pack', 'credits': 500, 'price': Decimal('39.00'), 'is_popular': True},
    {'name': 'Studio Pack', 'credits': 1500, 'price': Decimal('99.00'), 'is_popular': False},
    {'name': 'Agency Pack', 'credits': 5000, 'price': Decimal('299.00'), 'is_popular': False},
]

PLAN_PRICES = {'free': 0, 'starter': 19, 'professional': 49, 'enterprise': 199}


@login_required
def credits_view(request):
    packages = CreditPackage.objects.filter(active=True)
    if not packages.exists():
        packages = DEFAULT_PACKAGES  # fallback so page always renders nicely
    return render(request, 'payments/credits.html', {'packages': packages})


@login_required
@require_POST
def purchase_credits_view(request, package_name):
    package = next((p for p in DEFAULT_PACKAGES if p['name'] == package_name), None)
    db_package = CreditPackage.objects.filter(name=package_name, active=True).first()
    if db_package:
        credits_amount, price = db_package.credits, db_package.price
    elif package:
        credits_amount, price = package['credits'], package['price']
    else:
        messages.error(request, 'Unknown credit package.')
        return redirect('payments:credits')

    # NOTE: no real payment gateway is wired up. This simulates a
    # successful purchase so the credits/billing flow can be tested end
    # to end. Swap in a real payment processor call here.
    Transaction.objects.create(
        user=request.user,
        amount=price,
        status='completed',
        method='credits_purchase',
        description=f'Purchased {credits_amount} credits ({package_name})',
        credits_awarded=credits_amount,
    )
    request.user.add_credits(credits_amount)
    log_activity(request, request.user, 'credits_purchase', f'+{credits_amount} credits')

    messages.success(request, f'{credits_amount} credits added to your account!')
    return redirect('payments:credits')


@login_required
def billing_view(request):
    context = {
        'plans': PLAN_PRICES,
        'current_plan': request.user.subscription_plan,
    }
    return render(request, 'payments/billing.html', context)


@login_required
@require_POST
def change_plan_view(request, plan_key):
    if plan_key not in PLAN_PRICES:
        messages.error(request, 'Unknown plan.')
        return redirect('payments:billing')

    user = request.user
    user.subscription_plan = plan_key
    user.credits = settings.PLAN_CREDITS.get(plan_key, user.credits)
    user.save(update_fields=['subscription_plan', 'credits'])

    if PLAN_PRICES[plan_key] > 0:
        Transaction.objects.create(
            user=user,
            amount=Decimal(PLAN_PRICES[plan_key]),
            status='completed',
            method='subscription',
            description=f'Switched to {plan_key.title()} plan',
        )

    log_activity(request, user, 'plan_change', f'Changed plan to {plan_key}')
    messages.success(request, f'You are now on the {plan_key.title()} plan.')
    return redirect('payments:billing')


@login_required
def transactions_view(request):
    transactions = Transaction.objects.filter(user=request.user)
    return render(request, 'payments/transactions.html', {'transactions': transactions})
