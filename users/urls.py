from django.urls import re_path
from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
    re_path(r'^login/$', views.LoginView.as_view(), name='login'),
    re_path(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    re_path(r'^register/$', views.ClientRegistrationView.as_view(), name='register'),
    re_path(r'^add_doctor/$', views.DoctorRegistrationView.as_view(), name='add_doctor'),
    re_path(r'^delete_user/(?P<pk>\d+)/$', views.delete_user, name='delete_user'),
    re_path(r'^clients/$', views.ClientsView.as_view(), name='clients'),
    re_path(r'^doctors/$', views.DoctorsView.as_view(), name='doctors'),

    re_path(r'^attributes/$', views.DoctorAttributesView.as_view(), name='doctor_attributes'),
    re_path(r'^specialization/add/$', views.AddDoctorSpecializationView.as_view(), name='add_doctor_specialization'),
    re_path(r'^specialization/update/(?P<pk>\d+)/$', views.update_doctor_specialization, name='update_doctor_specialization'),
    re_path(r'^specialization/delete/(?P<pk>\d+)/$', views.delete_doctor_specialization, name='delete_doctor_specialization'),
    re_path(r'^category/add/$', views.AddDoctorCategoryView.as_view(), name='add_doctor_category'),
    re_path(r'^category/update/(?P<pk>\d+)/$', views.update_doctor_category, name='update_doctor_category'),
    re_path(r'^category/delete/(?P<pk>\d+)/$', views.delete_doctor_category, name='delete_doctor_category'),

    re_path(r'^doctor/edit/(?P<pk>\d+)/$', views.update_doctor, name='update_doctor'),
]   