from django.views.generic import TemplateView


class AppView(TemplateView):
    template_name = 'management/index.html'
    page = "management/btn_and_popup_{}.html".format('app')

    def get(self, request, *args, **kwargs):
        table = {
            'category': ['Name', 'Flavor', 'IP Address', 'Actions'],
            'rows': []
        }
        return self.render_to_response({
            'table': table,
            'page': self.page
        })

    def post(self, request, *args, **kwargs):
        table = {
            'category': ['App Name', 'Flavor', 'IP Address', 'Actions'],
            'rows': []
        }
        return self.render_to_response({
            'table': table,
            'page': self.page
        })


class NetworkView(TemplateView):
    template_name = 'management/index.html'
    page = "management/btn_and_popup_{}.html".format('network')

    def get(self, request, *args, **kwargs):
        table = {
            'category': ['Subnet ID', 'Name', 'CIDR', 'Provider', 'Security_group', 'Actions'],
            'rows': []
        }
        return self.render_to_response({
            'table': table,
            'page': self.page
        })

    def post(self, request, *args, **kwargs):
        table = {
            'category': ['Subnet ID', 'Name', 'CIDR', 'Provider', 'Security_group', 'Actions'],
            'rows': []
        }
        return self.render_to_response({
            'table': table,
            'page': self.page
        })


class ProviderView(TemplateView):
    template_name = 'management/index.html'
    page = "management/btn_and_popup_{}.html".format('provider')

    def get(self, request, *args, **kwargs):
        table = {
            'category': ['Name', 'Cloud Config', 'Actions'],
            'rows': []
        }
        return self.render_to_response({
            'table': table,
            'page': self.page
        })

    def post(self, request, *args, **kwargs):
        table = {
            'category': ['Name', 'Cloud Config', 'Actions'],
            'rows': []
        }
        return self.render_to_response({
            'table': table,
            'page': self.page
        })


class AboutView(TemplateView):
    template_name = 'management/about.html'

    def get(self, request, *args, **kwargs):
        table = {
            'category': ['App Name', 'Flavor', 'IP Address', 'Actions']
        }
        return self.render_to_response({})
