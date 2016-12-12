from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from management.models import Provider
from django.shortcuts import redirect


class AppView(LoginRequiredMixin, TemplateView):
    login_url = '/auth/login/'
    template_name = 'management/app.html'
    page = "management/btn_and_popup_{}.html".format('app')
    category =  ['Name', 'Flavor', 'IP Address', 'Actions']

    def get(self, request, *args, **kwargs):
        table = {
            'category': self.category,
            'rows': []
        }
        return self.render_to_response({
            'table': table,
            'page': self.page
        })

    def post(self, request, *args, **kwargs):
        table = {
            'category': self.category,
            'rows': []
        }
        return self.render_to_response({
            'table': table,
            'page': self.page
        })


class NetworkView(LoginRequiredMixin, TemplateView):
    login_url = '/auth/login/'
    template_name = 'management/network.html'
    page = "management/btn_and_popup_{}.html".format('network')
    category = ['Subnet ID', 'Name', 'CIDR', 'Provider', 'Security_group', 'Actions']

    def get(self, request, *args, **kwargs):
        table = {
            'category': self.category,
            'rows': []
        }
        return self.render_to_response({
            'table': table,
            'page': self.page
        })

    def post(self, request, *args, **kwargs):
        table = {
            'category': self.category,
            'rows': []
        }
        return self.render_to_response({
            'table': table,
            'page': self.page
        })


class ProviderView(LoginRequiredMixin, TemplateView):
    login_url = '/auth/login/'
    template_name = 'management/provider.html'
    page = "management/btn_and_popup_{}.html".format('provider')
    category = ['Name', 'Cloud Config', 'Actions']

    def _provider_to_tuple(self, providers):
        result = []
        for provider in providers:
            name = provider.name
            config = provider.config
            result.append((name, config, 'Not yet'))

        return result

    def get(self, request, *args, **kwargs):
        providers = Provider.objects.all()
        table = {
            'category': self.category,
            'rows': self._provider_to_tuple(providers)
        }
        return self.render_to_response({
            'table': table,
            'page': self.page
        })

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        config = request.POST.get('config')
        user_id = request.user.id
        if config:
            user = Provider(
                name=name,
                config=config,
                user_id=user_id
            )
            user.save()
        return self.get(request)

class AboutView(LoginRequiredMixin, TemplateView):
    template_name = 'management/about.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({})
