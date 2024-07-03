from django.urls import path

from MyApp import views

urlpatterns = [
    path('login', views.login_user), # http://www.example.com/login
    path('register', views.register_user),
    path('logout', views.logout_user),
    path('forgot_password', views.forgot_password),
    path('retrieve_password', views.retrieve_password),
    path('result/<str:matric_no>', views.get_current_semester_results),
    path('feedback', views.send_feedback),
    path('notifications', views.get_notifications),
    path('send_result/<str:matric_no>', views.get_and_send_current_semester_results_pdf),
]