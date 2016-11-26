from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.AppView.as_view(), name='default'),
    url(r'^network/', views.NetworkView.as_view(), name='network'),
    url(r'^app/', views.AppView.as_view(), name='app'),
    url(r'^provider/', views.ProviderView.as_view(), name='provider'),
    url(r'^about/', views.AboutView.as_view(), name='about'),
]
