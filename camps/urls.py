from django.urls import path
from . import views

app_name = 'camps'

urlpatterns = [
    path('nearest/', views.nearest_camp_view, name='nearest_camp'),
]
