from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^offers', views.offers, name='offers'),
    url(r'^company/(?P<comp_name>[a-zA-Z]+)$',views.company, name='company'),
    url(r'^category/(?P<cat_name>[a-zA-Z-]+)$',views.category, name='category'),
    url(r'^shop/(?P<offer_id>[0-9]+)$', views.shop, name='shop'),
    url(r'^mailoffers', views.mailoffers, name='mailoffers'), 
]
