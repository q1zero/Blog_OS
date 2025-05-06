from django.urls import path
from . import views

app_name = 'logs'

urlpatterns = [
    path('dashboard/', views.access_log_dashboard, name='dashboard'),
    path('apply-migrations/', views.apply_migrations, name='apply_migrations'),
]
