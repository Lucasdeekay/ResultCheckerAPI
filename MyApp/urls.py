from django.urls import path

from MyApp import views

urlpatterns = [
    path('login', views.login_user),
    path('register', views.register_user),
    path('logout', views.logout_user),
    path('forgot_password', views.forgot_password),
    path('retrieve_password', views.retrieve_password),
    path('result', views.get_current_semester_results),
]