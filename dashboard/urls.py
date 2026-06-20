from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.admin_dashboard_view, name='admin_dashboard'),
    path('user/', views.user_dashboard_view, name='user_dashboard'),
    path('users/<int:pk>/edit/', views.edit_user_view, name='edit_user'),
    path('moderate/<int:pk>/', views.moderate_report_view, name='moderate_report'),
    path('reports/<int:pk>/toggle-display/', views.toggle_report_display_view, name='toggle_report_display'),
    path('api/heatmap/', views.heatmap_data_api, name='heatmap_data_api'),
]
