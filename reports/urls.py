from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('submit/', views.submit_report_view, name='submit_report'),
    path('list/', views.report_list_view, name='report_list'),
    path('<int:pk>/', views.report_detail_view, name='report_detail'),
]
