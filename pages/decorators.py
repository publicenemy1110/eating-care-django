from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def approved_psychologist_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_approved_psychologist:
            messages.error(request, 'Управлять тестами могут только одобренные психологи.')
            return redirect('pages:tests')
        return view_func(request, *args, **kwargs)

    return _wrapped
