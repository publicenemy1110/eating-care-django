from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.StyledLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.StyledLogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('psychologists/<str:username>/', views.psychologist_public, name='psychologist_public'),
]
