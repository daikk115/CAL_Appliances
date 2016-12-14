import json

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
    cloud_config = {
        # this keyword must to match with type in model
        'ops': [
            'os_project_domain_name',
            'os_user_domain_name',
            'os_project_name',
            'os_username',
            # 'os_password',
            'os_auth_url'
        ],
        'aws': [
            'aws_access_key_id',
            # 'aws_secret_access_key',
            'region_name',
            'endpoint_url'
        ]
    }

    def _format_config(self, dd, level=0):
        """
        Support convert dict into html ul li tags
        :param dictObj:
        :param parent:
        :param indent:
        :return:

        E.G.: _printItems(dictObj, 'root', 0)
        """
        text = '<ul>'
        for k, v in dd.iteritems():
            text += '&nbsp;' * (4 * level) + \
                    '<li>%s: &nbsp;</li> %s' % (k, self._format_config(v, level + 1) if isinstance(v,dict) else (
            json.dumps(v) if isinstance(v, list) else v))

        text += '</ul>'
        return text

    def _provider_to_tuple(self, providers):
        """
        Convert provider object list to list of tupbles
        :param providers:
        :return:
        """
        items = []
        for provider in providers:
            id = provider.id
            name = provider.name

            config = dict(json.loads(provider.config))
            format = self._format_config(config)
            config['format'] = format

            enable = provider.enable
            type = provider.type
            items.append((id, name, config, enable, type))

        return items


    def _get_provider_config(self, request):
        """
        Get provider config when create or delete and push into dict
        :param request:
        :return:
        """
        cloud_type = request.POST.get('cloud')
        config_dict = {}
        if cloud_type:
            for attr in self.cloud_config.get(cloud_type):
                config_dict[attr] = request.POST.get(attr)

        return config_dict


    def get(self, request, *args, **kwargs):
        providers = Provider.objects.all()
        return self.render_to_response({
            'table': self._provider_to_tuple(providers)
        })


    def post(self, request, *args, **kwargs):
        """
        We have 3 case in this function: create, edit and change enable/disable
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        id = request.POST.get('id')
        check_enable = request.POST.get('check-enable')
        check = request.POST.get('check')

        if id:
            # Create or enable/disable exist provider
            provider = Provider.objects.get(id=id)
            if check_enable:
                # Enable/disable
                if check:
                    provider.enable = 1
                else:
                    provider.enable = 0
                provider.save()
                return self.get(request)
        else:
            # Crete provider
            provider = Provider()

        provider.name = request.POST.get('name')
        provider.config = json.dumps(
            self._get_provider_config(request)
        )
        provider.type = request.POST.get('cloud')
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
