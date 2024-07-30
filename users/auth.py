# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from .forms import LoginForm


def login_view(request):
    next_url = request.GET.get("next", "")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if next_url:
                    return HttpResponseRedirect(next_url)
                else:
                    return redirect("home") 
            else:
                form.add_error(None, "Invalid login credentials")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form, "next": next_url})
