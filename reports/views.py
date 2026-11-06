
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):

    user = request.user

    # Get the user's role.
    # Superusers are treated as administrators.
    if user.is_superuser:
        role = 'OWNER'
    else:
        profile = getattr(user, 'profile', None)
        role = profile.role if profile else 'CASHIER'

    context = {
        'role': role,
        'total_sales': 0,
        'total_transactions': 0,
        'total_products': 0,
        'low_stock': 0,
        'username': user.username,
    }

    return render(
        request,
        'dashboard.html',
        context
    )
