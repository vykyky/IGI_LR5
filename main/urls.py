from django.urls import path
from django.urls import re_path
from . import views

app_name = 'main'

urlpatterns = [
    path('services/', views.service_list, name = 'service_list'),
    path('<slug:category_slug>', views.service_list, name = 'service_list_by_category'),
    path('<int:id>/<slug:slug>', views.service_detail, name = 'service_detail'),
    path('add-category/', views.add_category, name='add_category'),
    path('add-service/<slug:category_slug>/', views.add_service, name='add_service'),
    path('service/<int:pk>/edit/', views.update_service, name='service_update'),
    path('service/<int:pk>/delete/', views.delete_service, name='service_delete'),

    path('', views.main_info, name='home'),
    path('about/', views.about_company, name='about'),
    path('news/', views.news_page, name='news'),
    path('dictionary/', views.dictionary_page, name='dictionary'),
    path('contacts/', views.contacts_page, name='contacts'),
    path('policy/', views.privacy_policy_page, name='policy'),
    path('vacancies/', views.vacancies_page, name='vacancies'),
    path('discounts/', views.discounts_page, name='discounts'),
    path('reviews/', views.ReviewsView.as_view(), name='reviews'),

    path('dictionary/add/', views.AddQuestionView.as_view(), name='add_question'),
    path('dictionary/answer/<int:pk>/', views.AddAnswerView.as_view(), name='add_answer'),

    path('vacancy/update/<int:pk>/', views.update_vacancy, name='update_vacancy'),
    path('vacancy/delete/<int:pk>/', views.delete_vacancy, name='delete_vacancy'),
    path('vacancy/add/', views.AddVacancyView.as_view(), name='add_vacancy'),

    path('doctor_profile/', views.ProfileDoctorView.as_view(), name='doctor_profile'),
    path('client_profile/', views.ProfileClientView.as_view(), name='client_profile'),
]
