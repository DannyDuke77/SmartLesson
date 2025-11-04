# accounts/decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check authentication
            if not request.user.is_authenticated:
                # Redirect to first role's login page
                first_role = roles[0] if roles else 'teacher'
                messages.error(request, "You must be logged in to access this page.")

                next_url = request.get_full_path()
                if next_url:
                    return redirect(f'/accounts/login/{first_role}/?next={next_url}')
                
                return redirect(f'/accounts/login/{first_role}/')

            # Check authorization (role match)
            user_role = getattr(request.user.profile, 'user_role', None)
            if user_role not in roles:
                messages.error(request, "You are not authorized to access this page.")
                return redirect('core:index')

            # Proceed to the view if checks pass
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
