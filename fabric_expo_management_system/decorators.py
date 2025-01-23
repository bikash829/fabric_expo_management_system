from django.shortcuts import redirect

def redirect_authenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('welcome')  # Redirect to the desired URL
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func