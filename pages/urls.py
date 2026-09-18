from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.index, name='index'),
    path('rpp/', views.rpp, name='rpp'),
    path('tests/', views.tests, name='tests'),
    path('tests/custom/create/', views.custom_test_create, name='custom_test_create'),
    path('tests/custom/<slug:slug>/edit/', views.custom_test_edit, name='custom_test_edit'),
    path('tests/custom/<slug:slug>/delete/', views.custom_test_delete, name='custom_test_delete'),
    path('tests/custom/<slug:slug>/', views.custom_test_take, name='custom_test_take'),
    path('tests/custom/<slug:slug>/result/', views.custom_test_result, name='custom_test_result'),
    path('tests/<slug:slug>/', views.screening_take, name='screening_take'),
    path('tests/<slug:slug>/result/', views.screening_result, name='screening_result'),
    path('parents/', views.parents, name='parents'),
    path('programs/', views.programs, name='programs'),
    path('about/', views.about, name='about'),
]
