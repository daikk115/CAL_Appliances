from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .forms import RegisterForm, LoginForm


class LoginView(TemplateView):
    template_name = 'authentication/login.html'

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return self.render_to_response({
            'form': form
        })

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # user = User.objects.get(username=username)
            # user.check()
            return HttpResponse("{}-{}".format(username, password))
        return self.render_to_response({})


class RegisterView(TemplateView):
    template_name = 'authentication/register.html'

    def get(self, request, *args, **kwargs):
        form = RegisterForm()
        return self.render_to_response({
            'form': form
        })

    def post(self, request, *args, **kwargs):
        return self.render_to_response({})
