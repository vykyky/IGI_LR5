from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:service_id>/', views.cart_add, name='cart_add'),
    path('remove/<str:key>/', views.cart_remove, name='cart_remove'),
    path('order/', views.make_order, name='make_order'),
]