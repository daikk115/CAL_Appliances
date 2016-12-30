import crypt
import json
from time import sleep
import imp
import socket;

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from management.models import Provider, Network, App
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from django.http import HttpResponse

from calplus import provider as calplus_provider
from calplus.client import Client


image_ids = {
        'openstack': '82eaaf2a-a417-4273-ae80-f44119013613',
        'amazon': 'ami-27e2ffd1'
    }

userdata_parameter = {
    'openstack': 'userdata',
    'amazon': 'UserData'
}

configurations = {
    'openstack': '2',
    'amazon': 'm1.small'
}

def format_config(dd, level=0):
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
                '<li>%s: &nbsp;</li> %s' % (k, format_config(v, level + 1) if isinstance(v, dict) else (
                    json.dumps(v) if isinstance(v, list) else v))

    text += '</ul>'

    return text


def format_userdata_start(name, image, script):
    userdata="""#!/bin/bash
./home/ubuntu/docker-1.10.0-dev -H tcp://127.0.0.1:2375 run -d -v /tmp:/tmp --name {} --security-opt seccomp:unconfined {} {}
""".format(name, image, script)
    return userdata


def format_userdata_migrate(name, image, script, ip):
    userdata="""#!/bin/bash
./home/ubuntu/docker-1.10.0-dev -H tcp://{}:2375 checkpoint --image-dir=/tmp/checkpoint1 {}
./home/ubuntu/docker-1.10.0-dev -H tcp://{}:2375 cp {}:/tmp/checkpoint1 /home/ubuntu/test_checkpoint
./home/ubuntu/docker-1.10.0-dev -H tcp://127.0.0.1:2375 create -v /tmp:/tmp --name {} --security-opt seccomp:unconfined {} {}
./home/ubuntu/docker-1.10.0-dev -H tcp://127.0.0.1:2375 restore --force=true --image-dir=/home/ubuntu/test_checkpoint {}
""".format(ip, name, ip, name, name, image, script, name)
    return userdata


def delete_pass(config):
    """ This is so stupid and temporary function
    """
    try:
        del config['os_password']
        del config['aws_secret_access_key']
    except Exception as e:
        pass


class AppView(LoginRequiredMixin, TemplateView):
    login_url = '/auth/login/'
    template_name = 'management/app.html'

    def get(self, request, *args, **kwargs):
        first_name = request.user.first_name
        last_name = request.user.last_name
        full_name = " ".join([first_name, last_name])
        providers = Provider.objects.filter(user_id=request.user.id)

        list_provider_id = []
        for provider in providers:
            list_provider_id.append(provider.id)

        apps = App.objects.filter(provider_id__in=list_provider_id)
        for app in apps:
            app.ip = json.loads(app.ip)
            setattr(app, 'config', format_config(
                {
                    'Docker Image': app.docker_image,
                    'Ports: ': app.ports
                }
            ))

        return self.render_to_response({
            'fullname': full_name,
            'apps': apps
        })

    def post(self, request, *args, **kwargs):
        """
        Action: create, edit, make network connect to external and delete network
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        id = request.POST.get('id')
        if id:
            # Get an exist provider
            app = App.objects.get(id=id)
            app.name = request.POST.get('name')
            app.ports = request.POST.get('ports')
            app.start_script = request.POST.get('start-script')
        else:
            # Crete provider
            app = App()

            # DATABASE
            app.name = request.POST.get('name')
            app.ports = request.POST.get('ports')
            app.start_script = request.POST.get('start-script')
            # Dont accept for change docker_image and network_id at this time
            # TODO: may be, we will support change network_id in future
            app.docker_image = request.POST.get('docker-image')
            app.network_id = request.POST.get('network-id')
            app.provider_id = request.POST.get('provider-id')

            # ON CLOUD
            provider = Provider.objects.get(id=app.provider_id)
            p = calplus_provider.Provider(provider.type,
                dict(json.loads(provider.config)))
            compute_client = Client(version='1.0.0',
                            resource='compute',
                            provider=p
                            )
            network_client = Client(version='1.0.0',
                            resource='network',
                            provider=p
                            )
            if provider.type == 'openstack':
                real_network_id = network_client.show(app.network_id).get('network_id')
            else:
                real_network_id = app.network_id

            kwargs = {
                "{}".format(userdata_parameter.get(provider.type)): format_userdata_start(
                    app.name, app.docker_image, app.start_script)
            }
            app.instance_id = compute_client.create(
                image_ids.get(provider.type), #id of Ubuntu Docker checkpoint v2 image
                configurations.get(provider.type), # Flavor
                real_network_id, # 
                None, 1,  # need two by lossing add default in base class
                **kwargs
            )
            sleep(5)
            app.ip = json.dumps(compute_client.list_ip(app.instance_id))

        app.save()

        return self.get(request)


class NetworkView(LoginRequiredMixin, TemplateView):
    login_url = '/auth/login/'
    template_name = 'management/network.html'

    def get(self, request, *args, **kwargs):
        first_name = request.user.first_name
        last_name = request.user.last_name
        full_name = " ".join([first_name, last_name])
        providers = Provider.objects.filter(user_id=request.user.id)

        list_provider_id = []
        for provider in providers:
            list_provider_id.append(provider.id)

        networks = Network.objects.filter(provider_id__in=list_provider_id)

        provider_name_dict = {}
        provider_config_dict = {}

        for provider in providers:
            provider_name_dict[provider.id] = provider.name

        for provider in providers:
            provider_config_dict[provider.id] = \
                dict(json.loads(provider.config))

        for network in networks:
            config = provider_config_dict.get(network.provider_id)
            delete_pass(config)
            setattr(network, 'provider_config', format_config(
                    config
                )
            )
            setattr(network, 'provider_name',
                provider_name_dict.get(network.provider_id))

        return self.render_to_response({
            'fullname': full_name,
            'networks': networks
        })

    def post(self, request, *args, **kwargs):
        """
        Action: create, edit, make network connect to external and delete network
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        id = request.POST.get('id')
        check_enable = request.POST.get('check-enable')
        check = request.POST.get('check')

        if id:
            # Get exist network
            network = Network.objects.get(id=id)
            network.name = request.POST.get('name')
        else:
            # Crete provider
            network = Network()
            # Dont accept change provider_id
            network.provider_id = request.POST.get('provider-id')
            network.name = request.POST.get('name')
            network.cidr = request.POST.get('cidr')
            provider = Provider.objects.get(id=network.provider_id)
            p = calplus_provider.Provider(provider.type,
                dict(json.loads(provider.config)))
            print p.config
            print p.type
            try:
                network_client = Client(version='1.0.0',
                                        resource='network',
                                        provider=p
                                    )
                net = network_client.create(network.name, network.cidr)
                gateway = network_client.connect_external_net(net.get('id'))
                network.network_id = net.get('id')
                network.internet_id = gateway
                del network_client
            except Exception as e:
                raise e

        network.save()
        return redirect("/network")


class ProviderView(LoginRequiredMixin, TemplateView):
    login_url = '/auth/login/'
    template_name = 'management/provider.html'
    cloud_config = {
        # this keyword must to match with type in model
        'openstack': [
            'os_project_domain_name',
            'os_user_domain_name',
            'os_project_name',
            'os_username',
            'os_password',
            'os_auth_url'
        ],
        'amazon': [
            'aws_access_key_id',
            'aws_secret_access_key',
            'region_name',
            'endpoint_url'
        ]
    }

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
            delete_pass(config)
            format = format_config(config)
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
        first_name = request.user.first_name
        last_name = request.user.last_name
        full_name = " ".join([first_name, last_name])
        providers = Provider.objects.filter(user_id=request.user.id)

        return self.render_to_response({
            'fullname': full_name,
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
            # Get or enable/disable exist provider
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
            # secret = request.POST.get('secret')
            # provider.secret = crypt.crypt(secret.encode('utf-8'), '$11$' + 'salt1234')

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


@login_required(login_url='/auth/login/')
def list_provider(request):
    providers = Provider.objects.filter(user_id=request.user.id, enable=1)
    response = ""
    for provider in providers:
        response += "<option value='{}'>{}</option>" .format(provider.id, provider.name)

    return HttpResponse(response)


@require_POST
def delete_network(request):
    id = request.POST.get('id')
    if id:
        network = Network.objects.get(id=id)
        try:
            provider = Provider.objects.get(id=network.provider_id)
            p = calplus_provider.Provider(provider.type,
                dict(json.loads(provider.config)))
            network_client = Client(version='1.0.0',
                                        resource='network',
                                        provider=p
                                    )
            internet_id = network.internet_id
            network_id = network.network_id
            network_client.disconnect_external_net(internet_id, network_id)
            network_client.delete(network_id)
            network.delete()
            del network_client
        except Exception as e:
            raise e
        finally:
            pass

    return redirect("/network")


@login_required(login_url='/auth/login/')
def list_network(request):
    provider_id = request.GET.get('provider_id')
    networks = Network.objects.filter(provider_id=provider_id)
    response = ""
    for network in networks:
        response += "<option value='{}'>{}</option>" .format(network.network_id, network.name)

    return HttpResponse(response)


@require_POST
def delete_app(request):
    id = request.POST.get('id')
    if id:
        app = App.objects.get(id=id)
        try:
            provider = Provider.objects.get(id=app.provider_id)
            p = calplus_provider.Provider(provider.type,
                dict(json.loads(provider.config)))
            compute_client = Client(version='1.0.0',
                            resource='compute',
                            provider=p
                            )
            compute_client.delete(app.instance_id)
            app.delete()
        except Exception as e:
            raise e
        finally:
            pass

    return redirect("/app")

@require_POST
def migrate_app(request):
    id = request.POST.get('id')
    if id:
        # Get an exist provider
        old_app = App.objects.get(id=id)

        # Crete provider
        app = App()

        # MIGRATE APP ON DATABASE
        app.name = old_app.name
        app.ports = old_app.ports
        app.start_script = old_app.start_script
        app.docker_image = old_app.docker_image
        app.network_id = old_app.network_id
        app.provider_id = old_app.provider_id

        # MIGRATE APP ON CLOUD
        provider = Provider.objects.get(id=app.provider_id)
        p = calplus_provider.Provider(provider.type,
            dict(json.loads(provider.config)))
        compute_client = Client(version='1.0.0',
                        resource='compute',
                        provider=p
                        )
        network_client = Client(version='1.0.0',
                        resource='network',
                        provider=p
                        )
        real_network_id_ops = network_client.show(app.network_id).get('network_id')
        public_ip =  json.loads(old_app.ip).get('PublicIps')[0]

        kwargs = {
            "{}".format(userdata_parameter.get(provider.type)): format_userdata_migrate(
                app.name, app.docker_image, app.start_script, public_ip)
        }
        app.instance_id = compute_client.create(
            image_ids.get(provider.type), #id of Ubuntu Docker checkpoint v2 image
            '2', # Flavor
            real_network_id_ops, # 
            None, 1,  # need two by lossing add default in base class
            **kwargs
        )
        sleep(5)
        app.ip = json.dumps(compute_client.list_ip(app.instance_id))
        app.save()

    return redirect("/app")

@require_POST
def add_public_ip(request):
    id = request.POST.get('id')
    if id:
        try:
            app = App.objects.get(id=id)
            # ON CLOUD
            provider = Provider.objects.get(id=app.provider_id)
            p = calplus_provider.Provider(provider.type,
                dict(json.loads(provider.config)))
            compute_client = Client(version='1.0.0',
                            resource='compute',
                            provider=p)
            network_client = Client(version='1.0.0',
                            resource='network',
                            provider=p)
            
            public_ip = network_client.allocate_public_ip()
            addr_id = public_ip.get('id')
            addr = public_ip.get('public_ip')

            ips = dict(json.loads(app.ip))
            ips['PublicIpIds'] = [addr_id]
            ips['PublicIps'] = [addr]
            app.ip = json.dumps(ips)

            compute_client.associate_public_ip(app.instance_id, addr_id)
            app.save()
        except:
            raise

    return redirect("/app")

@require_POST
def delete_public_ip(request):
    id = request.POST.get('id')
    if id:
        try:
            app = App.objects.get(id=id)
            # ON CLOUD
            provider = Provider.objects.get(id=app.provider_id)
            p = calplus_provider.Provider(provider.type,
                dict(json.loads(provider.config)))
            compute_client = Client(version='1.0.0',
                            resource='compute',
                            provider=p)
            network_client = Client(version='1.0.0',
                            resource='network',
                            provider=p)
            
            ips = dict(json.loads(app.ip))
            addr_id = ips['PublicIpIds'][0]
            del ips['PublicIpIds'][0]
            del ips['PublicIps'][0]
            app.ip = json.dumps(ips)

            compute_client.disassociate_public_ip(addr_id)
            network_client.release_public_ip(addr_id)
            app.save()
        except:
            raise

    return redirect("/app")

# @require_POST
# def change_secret(request):
#     id = request.POST.get('id')
#     old_secret = request.GET.get('old_secret')
#     new_secret = request.GET.get('new_secret')
#     if id:
#         provider = Provider.objects.get(id=id)
#         if crypt.crypt(old_secret.encode('utf-8'), '$11$' + 'salt1234') == provider.secret:
#             provider.secret = crypt.crypt(new_secret.encode('utf-8'), '$11$' + 'salt1234')
#         else:
#             # TODO: redirect + notif
#             pass

#     return redirect("/provider")
