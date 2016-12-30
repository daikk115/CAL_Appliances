from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.AppView.as_view(), name='default'),
    url(r'^network/', views.NetworkView.as_view(), name='network'),
    url(r'^app/', views.AppView.as_view(), name='app'),
    url(r'^provider/', views.ProviderView.as_view(), name='provider'),
    url(r'^about/', views.AboutView.as_view(), name='about'),
    url(r'^delete-provider/', views.delete_provider, name='delete-provider'),
    url(r'^list-provider/', views.list_provider, name='list-provider'),
    url(r'^delete-network/', views.delete_network, name='delete-network'),
    url(r'^list-network/', views.list_network, name='list-network'),
    url(r'^delete-app/', views.delete_app, name='delete-app'),
    url(r'^add-public-ip/', views.add_public_ip, name='add-public-ip'),
    url(r'^delete-public-ip/', views.delete_public_ip, name='delete-public-ip'),
    url(r'^migrate-app/', views.migrate_app, name='migrate-app'),
    # url(r'^change-secret/', views.change_secret, name='change-secret'),
]
