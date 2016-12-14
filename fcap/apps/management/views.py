from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from management.models import Provider
from django.views.decorators.http import require_POST
from django.shortcuts import redirect


class AppView(LoginRequiredMixin, TemplateView):
    login_url = '/auth/login/'
    template_name = 'management/app.html'

    def get(self, request, *args, **kwargs):
        first_name = request.user.first_name
        last_name = request.user.last_name
        full_name = " ".join([first_name, last_name])

        return self.render_to_response({
            'fullname': full_name,
        })

    def post(self, request, *args, **kwargs):
        return self.get(request)


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
        return self.get(request)


class ProviderView(LoginRequiredMixin, TemplateView):
    login_url = '/auth/login/'
    template_name = 'management/provider.html'

    def _provider_to_tuple(self, providers):
        items = []
        for provider in providers:
            id = provider.id
            name = provider.name
            config = provider.config
            enable = provider.enable
            items.append((id, name, config, enable))

        return items

    def get(self, request, *args, **kwargs):
        providers = Provider.objects.all()
        return self.render_to_response({
            'table': self._provider_to_tuple(providers)
        })

    def post(self, request, *args, **kwargs):
        id = request.POST.get('id')
        check = request.POST.get('check')
        if id:
            provider = Provider.objects.get(id=id)
        else:
            provider = Provider()

        if check:
            provider.enable = 1
        else:
            provider.enable = 0

        provider.name = request.POST.get('name')
        provider.config = request.POST.get('config')
        provider.user_id = request.user.id
        provider.save()

        return self.get(request)

class AboutView(LoginRequiredMixin, TemplateView):
    template_name = 'management/about.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({})

@require_POST
def delete_provider(request):
    id = request.POST.get('id')
    if id:
        Provider.objects.filter(id=id).delete()

    return redirect("/provider")
